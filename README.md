# cameraImage
read an rtsp video feed and extract an image for use in making timelapse video and website snapshot

I built this to work with a TP-link Tapo C320WS camera, but should work with any camera providing an RTSP feed.

It's not overly complicated, but assumes you're a bit competent with python, opencv and yaml. 

Copy example_config.yaml to config.yaml, and modify to suit your situation.

I call it once per minute with a cron job.
