#!/usr/bin/python
from pytapo import Tapo
from pytapo.media_stream.downloader import Downloader
import asyncio
import os
import datetime
from flock import flock

lock = flock('download_motions.lock', True).acquire()
if lock:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_motions())
else:
    print('exiting')
    exit()
    
outputDir = "/opt2/surveillance/eyeball2/motions/" #os.environ.get("OUTPUT")  # directory path where videos will be saved
host = "192.168.0.175" #os.environ.get("HOST")  # change to camera IP
password_cloud = "poopoopaper666" #os.environ.get("PASSWORD_CLOUD")  # set to your cloud password

# optional
window_size = os.environ.get(
    "WINDOW_SIZE"
)  # set to prefferred window size, affects download speed and stability, recommended: 50

print("Connecting to camera...")
tapo = Tapo(host, "admin", password_cloud, password_cloud)

async def download_motions():
    print("Getting recordings...")
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    for days in (0,1):
        date = now.strftime("%Y%m%d") 
        now -= delta 
        recordings = tapo.getRecordings(date)
        timeCorrection = tapo.getTimeCorrection()
        for recording in recordings:
            for key in recording:
                downloader = Downloader(
                    tapo,
                    recording[key]["startTime"],
                    recording[key]["endTime"],
                    timeCorrection,
                    outputDir,
                    None,
                    False,
                    window_size,
                )
                async for status in downloader.download():
                    statusString = status["currentAction"] + " " + status["fileName"]
                    if status["progress"] > 0:
                        statusString += (
                            ": "
                            + str(round(status["progress"], 2))
                            + " / "
                            + str(status["total"])
                        )
                    else:
                        statusString += "..."
                    print(
                        statusString + (" " * 10) + "\r",
                        end="",
                    )
                print("")
    
loop = asyncio.get_event_loop()
loop.run_until_complete(download_motions())
