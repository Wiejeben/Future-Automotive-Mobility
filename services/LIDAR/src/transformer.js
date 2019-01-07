import _ from 'lodash';
import { BitView } from 'bit-buffer';
const Transform = require('stream').Transform

const DEBUG = true; // process.env.NODE_ENV === 'development'

const START_FLAG = 0xA5;
const START_FLAG2 = 0x5A;

export const COMMANDS = _.mapValues({
    STOP: 0x25,
    RESET: 0x40,
    SCAN: 0x20,
    EXPRESS_SCAN: 0x82,
    FORCE_SCAN: 0x21,
    GET_INFO: 0x50,
    GET_HEALTH: 0x52,
    GET_SAMPLERATE: 0x59,
    GET_ACC_BOARD_FLAG: 0xFF,
    SET_MOTOR_PWM: 0xF0,
}, command => Buffer.from([START_FLAG, command]));

const RESPONSE_MODES = {
    SINGLE_REQUEST_SINGLE_RESPONSE: 0x0,
    SINGLE_REQUEST_MULTIPLE_RESPONSE: 0x1,
    RESERVED_3: 0x3,
    RESERVED_$: 0x4,
    NO_RESPONSE: 5,
};

const RESPONSES = {
    SCAN_START: {
        responseMode: RESPONSE_MODES.SINGLE_REQUEST_MULTIPLE_RESPONSE,
        bytes: [START_FLAG, START_FLAG2, 0x05, 0x00, 0x00, 0x40, 0x81],
    },
    HEALTH: {
        responseMode: RESPONSE_MODES.SINGLE_REQUEST_SINGLE_RESPONSE,
        bytes: [START_FLAG, START_FLAG2, 0x03, 0x00, 0x00, 0x00, 0x06],
        dataLength: 3, // Bytes
    },
    INFO: {
        responseMode: RESPONSE_MODES.SINGLE_REQUEST_SINGLE_RESPONSE,
        bytes: [START_FLAG, START_FLAG2, 0x14, 0x00, 0x00, 0x00, 0x04],
        dataLength: 20,
    },
};

export const REPLIES = {
    HEALTH: 'health',
    INFO: 'info',
    START_SCAN: 'start-scan',
    BOOT: 'boot',
    MEASUREMENT: 'measurement',
    ERROR: 'error',
}

export default class RPLidarTransformer extends Transform {
    constructor(options = {}) {
        options = {
            ...options,
            objectMode: true,
        }

        super(options)

        this.buffer = new Buffer(0)
    }

    _transform(chunk, encoding, cb) {
        if (this.isHealthCheckResponse(chunk)) {
            this.push({
                type: REPLIES.HEALTH,
                data: {
                    status: parseInt(`${this.hexToBinaryString(chunk[7])}`, 2),
                    errorCode: parseInt(`${this.hexToBinaryString(chunk[9])}${this.hexToBinaryString(chunk[8])}`, 2)
                }
            });

            return cb()
        }

        if (this.isInfoCheckResponse(chunk)) {
            this.push({
                type: REPLIES.INFO,
                data: this.parseInfo(chunk)
            });

            return cb()
        }

        // Make it call _flush?
        if (this.isScanStart(chunk)) {
            this.buffer = new Buffer(0);

            this.push({
                type: REPLIES.SCAN_START,
                data: {},
            });

            return cb()
        }

        if (this.isBootUpMessage(chunk)) {
            this.push({
                type: REPLIES.BOOT,
                data: String(chunk)
            });

            return cb()
        }

        if (chunk.length === 256) {
            try {
                // add any extra bytes left off from the last buffer
                let data = Buffer.concat([this.buffer, chunk]);
                let dataLength = data.length;
                let extraBits = dataLength % 5;

                for (let offset = 0; offset < dataLength - extraBits; offset += 5) {
                    this.push({
                        type: REPLIES.MEASUREMENT,
                        data: this.parseScan(data.slice(offset, offset + 5))
                    });
                }

                // add any bits that don't make up a complete data packet to the cache
                this.buffer = data.slice(dataLength - extraBits, dataLength);
            } catch (err) {
                this.push({
                    type: REPLIES.ERROR,
                    data: err
                });
            }

            return cb()
        }

        if (DEBUG) {
            console.log('Unknown packet (' + chunk.length + ')', chunk);
        }

        return cb()
    }

    _flush(cb) {
        this.buffer = new Buffer(0)
        cb();
    }

    isHealthCheckResponse(chunk) {
        if (chunk.length !== 10) return false;

        return chunk[0] === START_FLAG
            && chunk[1] === 0x5A
            && chunk[2] === 0x03
            && chunk[3] === 0x00
            && chunk[4] === 0x00
            && chunk[5] === 0x00
            && chunk[6] === 0x06;
    }

    isInfoCheckResponse(buffer) {
        if (buffer.length !== RESPONSES.INFO.bytes.length + RESPONSES.INFO.dataLength) return false;

        for (let i = 0; i < RESPONSES.INFO.bytes.length; i++) {
            if (buffer[i] !== RESPONSES.INFO.bytes[i]) return false;
        }

        return true;
    }

    isScanStart(buffer) {
        if (buffer.length !== 7) return false;

        return buffer[0] === START_FLAG
            && buffer[1] === 0x5A
            && buffer[2] === 0x05
            && buffer[3] === 0x00
            && buffer[4] === 0x00
            && buffer[5] === 0x40
            && buffer[6] === 0x81;
    }

    isBootUpMessage(buffer) {
        if (buffer.length !== 56) return false;

        return buffer[0] === 0x52
            && buffer[1] === 0x50
            && buffer[2] === 0x20
            && buffer[3] === 0x4c
            && buffer[4] === 0x49
            && buffer[5] === 0x44
            && buffer[6] === 0x41
            && buffer[7] === 0x52;
    }

    hexToBinaryString(hex) {
        return _.padStart((hex >>> 0).toString(2), 8, '0');
    }

    parseInfo(buffer) {
        return {
            model: buffer[7],
            firmware_minor: buffer[8],
            firmware_major: buffer[9],
            hardware: buffer[10],
            serial_number: _.reduce(buffer.slice(11, 27), (acc, item) => `${acc}${item.toString(16)}`, ''),
        };
    }

    parseScan(data) {
        let byte0 = this.hexToBinaryString(data[0]);
        let byte1 = this.hexToBinaryString(data[1]);
        let byte2 = this.hexToBinaryString(data[2]);
        let byte3 = this.hexToBinaryString(data[3]);
        let byte4 = this.hexToBinaryString(data[4]);

        let bb = new BitView(data);

        // if (DEBUG) console.log(`${byte0} ${byte1} ${byte2} ${byte3} ${byte4}`);

        let quality = bb.getBits(2, 6, false);

        let start = Boolean(parseInt(byte0.substring(7, 8), 2));
        let inverseStart = Boolean(parseInt(byte0.substring(6, 7), 2));
        if (start === inverseStart) throw new Error('ParseError: !S === S');

        let C = byte1.substring(7, 8);
        if (C != 1) throw new Error('ParseError: C not 1');

        let angle = bb.getBits(9, 15, false) / 64.0; // 0-360 deg
        // I've noticed that sometimes it gives me an angle slightly over 360
        if (angle > 360 && angle < 361) angle = angle - 360;
        if (angle < 0 || angle > 360) throw new Error(`ParseError: Angle parsed outside 0-360 range (${angle})`);

        let distance = bb.getBits(24, 16, false) / 4.0; // mm

        return {
            start,
            quality,
            angle,
            distance
        };
    }
}
