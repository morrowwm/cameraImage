#!/usr/bin/python3

import time
import datetime
import os
import cv2
import subprocess
import yaml
import ephem
import math

global capture
global config
config={}
capture = None

def do_image():
    capture = cv2.VideoCapture(config['rtsp_url'])

    if capture.isOpened():       
    
        # Get the original frame size
        frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate the crop coordinates
        crop_x = 0
        crop_y = 0
        crop_width = min(frame_width, 1920)
        crop_height = min(frame_height, 1080)

        # Read the current frame from the video stream
        ret, frame = capture.read()
        capture.release()

        # if the frame was read successfully, prepare output images
        if ret:
            # Timestamp and save the frame as a JPEG image
            timestamp = time.strftime("%Y-%m-%d %H:%M")
            text_pos = [1372, 1420, 2048, 2648]
            text_region = frame[text_pos[0]:text_pos[1], text_pos[2]: text_pos[3]]
            brightness = cv2.mean(text_region) 
            font_color = [0, 0, 0]
            for i in [0, 1, 2]:
                if brightness[i] < 128: font_color[i] = 255

            cv2.putText(frame, timestamp,
                (text_pos[2], text_pos[1]),  # bottom left corner of text 
                cv2.FONT_HERSHEY_SIMPLEX, # font 
                1.5, # font scale
                font_color, # font color
                3, # thickness
                2) # lineType

            timestamp = time.strftime("%Y%m%d%H%M%S")

            filename = f"{config['image_dir']}/eye2-{timestamp}.jpeg"
            # copy over to server for building timelapse movie
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            p = subprocess.Popen(["/usr/bin/scp", filename, config['timelapse_dir']])
            status = os.waitpid(p.pid, 0)
            print(f"Saved frame {filename} to {config['timelapse_dir']}")
            # if sunrise save that especially
            here = ephem.Observer()
            here.date = ephem.now()
            here.lon  = math.radians(config['longitude'])
            here.lat  = math.radians(config['latitude'])
            here.elev = config['elevation']
            # adjust for US Naval Almanac sunrise definition
            here.pressure= 0
            here.horizon = '-0:34'
            sunrise=here.previous_rising(ephem.Sun()).datetime() #Sunrise
            sunset =here.next_setting   (ephem.Sun()).datetime() #Sunset
            now = here.date.datetime()
            offset = 27
            before = sunrise+datetime.timedelta(minutes=offset)
            after = sunrise+datetime.timedelta(minutes=offset+1)
            print("sunrise: {}\nbefore: {}\nafter: {}\nnow: {}\n".format(sunrise.strftime("%H:%M:%S"), 
                                                                         before.strftime("%H:%M:%S"), 
                                                                         after.strftime("%H:%M:%S"), 
                                                                         now.strftime("%H:%M:%S")))
            if before <= now <= after:
                pic_time = now.strftime("%Y-%m-%d %H:%M:%S")
                p = subprocess.Popen(["/usr/bin/scp", filename, config['sunrise_dir']])
                status = os.waitpid(p.pid, 0)
                print(f"Saved frame {filename} to {config['sunrise_dir']}")

            # process, and copy over to server for use in website page
            website_image = cv2.resize(frame, (720,405))

            # CLAHE - not being used
            #lab_image = cv2.cvtColor(website_image, cv2.COLOR_BGR2LAB)
            #l, a, b = cv2.split(lab_image)
            # clipLimit -> Threshold for contrast limiting
            #clahe = cv2.createCLAHE(clipLimit=1.5)
            #leq = clahe.apply(l)
            #lab_image = cv2.merge((leq,a,b))
            #website_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)

            filename = config['snapshot_file']
            cv2.imwrite(filename, website_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            p = subprocess.Popen(["/usr/bin/scp", filename, config['website_dir']])
            status = os.waitpid(p.pid, 0)

        else:
            print("Error reading frame")
    else:
        print("Error opening video stream")

if __name__ == "__main__":
    with open("config.yaml", 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    do_image()
