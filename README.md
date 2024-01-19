# cameraImage
Read an rtsp video feed, extract image for use in making timelapse video and website snapshot and write to the appropriate directories.

I built this to work with a TP-link Tapo C320WS camera, but should work with any camera providing an RTSP feed.

It's not overly complicated, but assumes you're a bit competent with python, opencv and yaml. I'm no guru, so have tried to limit anything overly elegant.

* Copy example_config.yaml to config.yaml, and modify to suit your situation.
* create the any directories needed for your configuration, both local and on remote servers
* Change the cameraImage.py file to be executable.
* Install any necessary python libraries.

I call it once per minute with a cron job.

`* * * * * cd /home/fred/bin; /home/fred/bin/cameraImage.py`

Thanks to https://www.briandorey.com/post/tplink-tapo-tc65-camera-capture-opencv-webcam for the starting point.

## Utilities
segmentAssemble.py merges the timelapse images and any motion videos together into one integrated video. 
* create directories ./motion and ./assemble under the directory holding your timelapse images
download_motions.py syncs the motion detection videos on the camera onto your server
* I use a cronjab every 5 minutes to do this
  ** `5,15,25,35,45,55 * * * * /home/fred/bin/download_motions.py`
  
Each day after 0600h, run `python segmentAssemble.py`, then go into the assemble directory and run `bash assemble.sh`. On my poor old PC, it typically takes most of an hour to process. My GPU cannot handle 2K video size. Update: limiting motion videos to their first ten seconds helps.
