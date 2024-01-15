from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time
import pathlib

assemble_file = open('assemble/assemble.sh', 'w')
concat_list = open('assemble/concat_list.txt', 'w')

'''
TODO see if GPU can be used
ffmpeg -hwaccel vaapi -hwaccel_output_format vaapi -hwaccel_device /dev/dri/renderD128 -i input.mp4 -c:v h264_vaapi output.mp4

[h264 @ 0x559c91785c00] Hardware does not support image size 2560x1440 (constraints: width 0-2048 height 0-1152).
[h264 @ 0x559c91785c00] Failed setup for format vaapi_vld: hwaccel initialisation returned error.
Impossible to convert between the formats supported by the filter 'Parsed_null_0' and the filter 'auto_scaler_0'
Error reinitializing filters!
Failed to inject frame into filter network: Function not implemented

'''


dir_path = '.'
# 4 times speed, resample to 30fps, remove audio, only first ten seconds of motion video. Don't overwrite existing
video_ffmpeg = '/usr/bin/ffmpeg -i "{0}" -r 30 -filter:v "setpts=PTS/4,fps=30,{1}" -an -n -ss 0 -t 10 -vcodec libx265 segment{2:03d}.mkv\n'
# concatenate images into a video segment. frame rate is defined in input list
image_ffmpeg = '/usr/bin/ffmpeg -safe 0 -r 30 -f image2 -f concat -i {0} -vcodec libx265 -n segment{1:03d}.mkv\n'
# text format for timestamp on motion video (I don't like the timestamp provided by the camera)
video_text = 'drawtext=text=\'{0}\':x=48:y=48:fontsize=32:fontcolor=white'
# final concatenation of all video segments
final_ffmpeg = '/usr/bin/ffmpeg  -f concat -safe 0 -i concat_list.txt -c copy -y {0}_output.mkv\n'

old_names = list(pathlib.Path('./old/').glob('eye2-*.jpeg')) # timelapse images already moved out from working folder
img_names = list(pathlib.Path('.').glob('eye2-*.jpeg'))
vid_names = list(pathlib.Path('./motions/').glob('*.mp4')) # motion detection videos

stats = ((os.stat(path), path) for path in old_names + img_names + vid_names)
files = ((stat[ST_CTIME], path) for stat, path in stats if S_ISREG(stat[ST_MODE]))

# use the appropriate part of file name for each file's start time. file system creation time can change, so we can't use it
files = list(files)
for index, row in enumerate(files):
    cdate, path = row
    timestr=os.path.basename(path)
    if path.suffix == ".mp4":
        timestr = timestr[0:19]
        dt_format = "%Y-%m-%d %H_%M_%S"
        video_start_time = time.mktime(time.strptime(timestr, dt_format)) - 4*3600
    elif path.suffix == ".jpeg":
        timestr = timestr[5:19]
        dt_format = "%Y%m%d%H%M%S"
        video_start_time = time.mktime(time.strptime(timestr, dt_format))
    swap in the new row
    temp=list(files[index])
    temp[0] = video_start_time
    files[index] = tuple(temp)

# start at 6AM yesterday, end this morning
start6am = (int(time.time() // 86400)) * 86400 - 3600*14  # 6am local time yesterday: TODO, handle DST
end6am = start6am + 24*3600

segment = 0
inputs = ''

for cdate, path in sorted(files):
    if cdate>start6am and cdate <= end6am:
        timestamp = time.strftime("%Y-%m-%d %H\:%M", time.localtime(cdate))  # need to escape ":" for use in ffmpeg below
        print(segment, start6am, timestamp, " file: ", path.resolve())
        # for an image, add to the list of images that will form a timelapse video segment
        if path.suffix == ".jpeg":
            # print("\t is a snapshot image")
            inputs += 'file {0!s}\nduration 0.0333333\n'.format(path.resolve())
        elif path.suffix == ".mp4":
            # print("\t is a motion video")
            # create inputs list file for any queued up images preceding this motion video
            # then reset for next batch
            if len(inputs) > 0:
                filename = 'inputs{0:03d}'.format(segment)
                with open( filename, 'w') as f:
                    f.write(inputs)
                    f.close()
                    assemble_file.write(image_ffmpeg.format(filename, segment))
                    concat_list.write('file segment{0:03d}.mkv\n'.format(segment))
                segment = segment+1
                inputs = ""
            # then output video at faster speed and preview first few seconds. Also add a timestamp
            timebanner = video_text.format(timestamp)
            assemble_file.write('# preceded by images epoch {}\n'.format(cdate))
            assemble_file.write(video_ffmpeg.format(path.resolve(), timebanner, segment))
            concat_list.write('file segment{0:03d}.mkv\n'.format(segment))
            segment = segment+1
        else:
            print(f"{path.resolve()} is unknown type")

# finish off any remaining timestamp
if len(inputs) > 0:
    filename = 'inputs{0:03d}'.format(segment)
    with open( filename, 'w') as f:
        f.write(inputs)
        f.close()
        assemble_file.write(image_ffmpeg.format(filename, segment))
        concat_list.write('file segment{0:03d}.mkv\n'.format(segment))

concat_list.close()

timestamp = time.strftime("%Y-%m-%d", time.localtime(start6am))
assemble_file.write(final_ffmpeg.format(timestamp))
assemble_file.close()
# assemble shell script can now be run
