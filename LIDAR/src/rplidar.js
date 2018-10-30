import _ from 'lodash';
import SerialPort from 'serialport';
import { BitView } from 'bit-buffer';
import { EventEmitter } from 'events';
import RPLidarTransformer, { COMMANDS, REPLIES } from './transformer';

const DEBUG = true; // process.env.NODE_ENV === 'development'

/**
 * Windows: COM3
 * macOS: /dev/tty.SLAB_USBtoUART
 * Linux: /dev/ttyUSB0
*/
const DEFAULT_SERIALPORT_PATH = '/dev/ttyUSB0';

const RPLIDAR_STATES = {
    UNKNOWN: 0,
    IDLE: 1,
    PROCESSING: 2,
    SCANNING: 3,
    STOP: 4
};

const MOTOR_STATES = {
    OFF: 0,
    ON: 1
};

const HEALTH_STATUSES = new Map();
HEALTH_STATUSES.set(0x00, 'Good');
HEALTH_STATUSES.set(0x01, 'Warning');
HEALTH_STATUSES.set(0x02, 'Error');

export default class RPLidar extends EventEmitter {
    state = RPLIDAR_STATES.UNKNOWN;
    motorState = MOTOR_STATES.OFF;

    debugWaitingFor;
    serial;
    parser;

    constructor(path = DEFAULT_SERIALPORT_PATH, options = {}) {
        super();

        this.path = path;
        this.debug = !!options.debug;
    }

    /**
     * Initializes the SerialPort connection and setup Event watchers.
     */
    async init() {
        if (this.serial) throw new Error('SerialPort instance already exist');

        // Connect to LIDAR
        this.serial = new SerialPort(this.path, {
            baudRate: 115200,
            buffersize: 256,
        });

        // Apply data parser.
        this.parser = this.serial.pipe(new RPLidarTransformer());
        this.parser.on('data', ({type, data}) => {
            if (type === REPLIES.MEASUREMENT) {
                console.log(data)
                return;
            }

            this.emit(type, data)
        });

        // Emit events to outer layer
        this.serial.on('error', (err) => this.emit('error', err));
        this.serial.on('disconnect', () => this.emit('disconnect'));
        this.serial.on('close', () => this.emit('close'));

        // Open connection
        return new Promise((resolve, reject) => {
            this.serial.on('open', () => {
                this.serial.flush(err => {
                    if (err) return reject(err);

                    this.state = RPLIDAR_STATES.IDLE;

                    this.emit('ready');
                    resolve();
                });
            });
        });
    }

    /**
     * Get health data of the LIDAR.
     */
    async getHealth() {
        this.state = RPLIDAR_STATES.PROCESSING;
        this.debugWaitingFor = REPLIES.HEALTH;
        this.serial.write(COMMANDS.GET_HEALTH);

        return new Promise((resolve, reject) => {
            this.once(REPLIES.HEALTH, health => {
                resolve(health);
                this.debugWaitingFor = false;
            });
        });
    }

    /**
     * Get device information about the LIDAR.
     */
    async getInfo() {
        this.state = RPLIDAR_STATES.PROCESSING;
        this.debugWaitingFor = 'INFO';
        this.serial.write(COMMANDS.GET_INFO);

        return new Promise((resolve, reject) => {
            this.once(REPLIES.INFO, info => {
                resolve(info);
                this.debugWaitingFor = false;
            });
        });
    }

    /**
     * Resets the RPLidar.
     */
    async reset() {
        this.serial.write(COMMANDS.RESET);

        return new Promise(resolve => {
            this.once(REPLIES.BOOT, (/*bootMessage*/) => {
                // if debug log bootMessage
                resolve();
            });
        });
    }

    /**
     * Starts motor to rotate the LIDAR.
     */
    async startMotor() {
        this.serial.set({ dtr: false });
        this.motorState = MOTOR_STATES.ON;

        return wait(5);
    }

    /**
     * Stops the motor to halt the LIDAR.
     */
    async stopMotor() {
        this.serial.set({ dtr: true });
        this.motorState = MOTOR_STATES.OFF;

        return wait(5);
    }

    /**
     * Starts scan to gather LIDAR data.
     */
    async scan() {
        await this.startMotor();

        // Start scan
        this.state = RPLIDAR_STATES.PROCESSING;
        this.debugWaitingFor = 'SCAN_START';
        this.serial.write(COMMANDS.SCAN);

        return new Promise(resolve => {
            this.once(REPLIES.START_SCAN, () => {
                this.state = RPLIDAR_STATES.SCANNING;
                this.debugWaitingFor = 'SCAN';
                resolve();
            });
        });
    }

    /**
     * Stop all operations.
     */
    async stop() {
        this.serial.write(COMMANDS.STOP);
        await wait(10);
        return this.stopMotor();
    }
}

/**
 * Handy wait function to prevent code execution going too quick for the LIDAR.
 */
async function wait(time) {
    return new Promise(respond => {
        setTimeout(respond, time);
    });
}
