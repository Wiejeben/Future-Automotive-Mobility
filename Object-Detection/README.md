# Object Detection

Applies Tensorflow object detection to webcam video stream.

# Installation:

Make sure you are running Linux. This is required since Docker does not support device passthrough on other operating systems.
Also make sure you have Docker up and running.

To build the Docker image, execute:
> ./build.sh

To run the Docker image, execute:
> ./start.sh

You may also execute the `docker-compose` commands directly, however in order to show a display `xhost +` has to be executed first.
 

All possible arguments are:

```
-d (--display), type=int, default=0: Whether or not frames should be displayed

-I (--input-device), type=int, default=0: Device number input

-w (--num-workers), type=int, default=2: Number of workers

-q-size (--queue-size), type=int, default=5: Size of the queue

-l (--logger-debug), type=int, default=0: Print logger debug

```
