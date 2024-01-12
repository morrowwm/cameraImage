#!/usr/bin/python3

from __future__ import absolute_import, division, print_function, unicode_literals
import time
import datetime as dt
import os
import cv2
import traceback
import threading
import subprocess
import yaml

config={}

# I'm not using this. Nothing needs blurring, but maybe in the future
blur1_x = 0  # X-coordinate of the top-left corner of the blur region
blur1_y = 0  # Y-coordinate of the top-left corner of the blur region
blur1_width = 100  # Width of the blur region
blur1_height = 100  # Height of the blur region

blur2_x = 0  # X-coordinate of the top-left corner of the blur region
blur2_y = 0  # Y-coordinate of the top-left corner of the blur region
blur2_width = 100  # Width of the blur region
blur2_height = 100  # Height of the blur region

capture = None

def blur_region(frame, x, y, width, height):
    # Create a region of interest (ROI) for blurring
    roi = frame[y:y+height, x:x+width]

    # Apply Gaussian blur to the ROI
    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 0)

    # Replace the ROI with the blurred version
    frame[y:y+height, x:x+width] = blurred_roi

    return frame

def get_image():
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

        # Check if the frame was read successfully
        if ret:
            # Crop the frame - maybe resize? 
            # frame = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]

            # Blur the specified regions of the frame
            #frame = blur_region(frame, blur1_x, blur1_y, blur1_width, blur1_height)
            #frame = blur_region(frame, blur2_x, blur2_y, blur2_width, blur2_height) 

            # Timestamp and save the frame as a JPEG image
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            text_region = frame[16:48, 32:512]
            brightness = cv2.mean(text_region) 
            font_color = [0, 0, 0]
            for i in [0, 1, 2]:
                if brightness[i] < 128: font_color[i] = 255

            cv2.putText(frame, timestamp,
                (48, 48),  # bottom left corner of text 
                cv2.FONT_HERSHEY_SIMPLEX, # font 
                1.5, # font scale
                font_color, # font color
                3, # thickness
                2) # lineType

            timestamp = time.strftime("%Y%m%d%H%M%S")

            filename = f"{config['image_folder']}/eye2-{timestamp}.jpeg"
            # copy over to server for building timelapse movie
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            p = subprocess.Popen(["/usr/bin/scp", filename, config['timelapse_dir']])
            status = os.waitpid(p.pid, 0)
            print(f"Saved frame {filename} to {config['timelapse_dir']}")

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

        capture.release()
    else:
        print("Error opening video stream")

    # not using this, just call from crontab every minute
    # restart_thread()

def restart_thread():
    st = threading.Timer(config['capture_interval'], get_image)
    st.daemon = True
    st.start()

def main():
    '''
    Main program function
    '''
    global capture
    global config

    get_image()

    # just execute it once, and schedule script in crontab
    #while (True):
    #    time.sleep(1)


if __name__ == "__main__":
    #with open("config.yaml", 'w') as yamlfile:
    #    data = yaml.dump(config, yamlfile)
    #    print("Write successful")
    with open("config.yaml", 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    main()
