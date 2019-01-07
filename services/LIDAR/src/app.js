import RPLidar from './rplidar';

const lidar = new RPLidar();

lidar.init().then(async () => {
    let health = await lidar.getHealth();
    console.log('health: ', health);

    let info = await lidar.getInfo();
    console.log('info: ', info);

    await lidar.scan();
    console.log('started scanning');
}).catch((e) => {
    console.error(e);
});
