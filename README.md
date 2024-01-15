# cameraImage
Read an rtsp video feed, extract image for use in making timelapse video and website snapshot and write to the appropriate directories.

I built this to work with a TP-link Tapo C320WS camera, but should work with any camera providing an RTSP feed.

It's not overly complicated, but assumes you're a bit competent with python, opencv and yaml. I'm no guru, so have tried to limit anything overly elegant.

* Copy example_config.yaml to config.yaml, and modify to suit your situation.
* Change the cameraImage.py file to be executable.
* Install any necessary python libraries.

I call it once per minute with a cron job.

`* * * * * cd /home/fred/bin; /home/fred/bin/cameraImage.py`

Thanks to https://www.briandorey.com/post/tplink-tapo-tc65-camera-capture-opencv-webcam for the starting point.

segmentAssemble.py merges the timelapse images nd any motion videos together into one integrated video. 
* create directories ./motion and ./assemble nder the directory holding your timelapse images
* sync the motion detection videos from the camera into the motion directory. I use a cronjab every 5 minutes
* after 6:00AM, `python segmentAssemble.py`, then go into the assemble directory and run `bash assemble.sh`. On my poor old PC, it takes most of an hour to create it all.
