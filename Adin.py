import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size
import atexit
from pathlib import Path
import time
import sys
import os

#--------setting up the folder structure

home = str(Path.home())

root = os.path.join(home, "Desktop", "AdInsertion")
if not os.path.exists(root):
    os.makedirs(root)
    print("Root folder created")
else:
    print("Root folder already exists")

path_source = os.path.join(home, "Desktop", "AdInsertion", "Source")
if not os.path.exists(path_source):
    os.makedirs(path_source)
    print("Source folder created")
else:
    print("Source folder already exists")

path_transform = os.path.join(home, "Desktop", "AdInsertion", "Converted")
if not os.path.exists(path_transform):
    os.makedirs(path_transform)
    print("Converted folder created")
else:
    print("Converted folder already exists")

#------------------------setting up the operation files
input_file = os.path.join("\source", "main.mp4")
ad1_file = os.path.join("\source", "1.mp4")
ad2_file = os.path.join("\source", "2.mp4")

out_main = os.path.join("\converted", "output_main_file")
out_ad1 = os.path.join("\converted", "output_ad1_file")
out_ad2 = os.path.join("\converted", "output_ad2_file")

video_main = ffmpeg_streaming.input(root+input_file)
video_ad1 = ffmpeg_streaming.input(root+ad1_file)
video_ad2 = ffmpeg_streaming.input(root+ad2_file)

root_main = (os.path.join(root+out_main))
root_ad1 = (os.path.join(root+out_ad1))
root_ad2 = (os.path.join(root+out_ad2))


def video_to_hls():

    _480p = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))

    # main video to HLS Conversion
    hls_main = video_main.hls(Formats.h264())
    hls_main.representations(_480p)
    with open('output_main_file.m3u8', 'w+') as fp:
        pass
    hls_main.output(root_main)
    atexit.register(print, "Main video conversion successful!")

    # ad1 video to HLS Conversion
    hls_ad1 = video_ad1.hls(Formats.h264())
    hls_ad1.representations(_480p)
    with open('output_ad1_file.m3u8', 'w+') as fp:
        pass
    hls_ad1.output(root_ad1)
    atexit.register(print, "AD1 video conversion successful!")

    # ad2 video to HLS Conversion
    hls_ad2 = video_ad2.hls(Formats.h264())
    hls_ad2.representations(_480p)
    with open('output_ad2_file.m3u8', 'w+') as fp:
        pass
    hls_ad2.output(root_ad2)
    atexit.register(print, "AD2 video conversion successful!")


def hls_enc():
    print("HLS files generation and generating encryption key in process...")
    _480p = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))

    #A path you want to save a random key to your local machine
    save_to = root+'/key'

    #A URL (or a path) to access the key on your website
    url = 'http://www.localhost.com/test2/key'
    # or url = '/"PATH TO THE KEY DIRECTORY"/key';

    #creating hls encrypted file for main video
    main_hls = video_main.hls(Formats.h264())
    main_hls.encryption(save_to, url)
    main_hls.representations(_480p)
    main_hls.output(os.path.join(path_transform+'\hls_main.m3u8'))

    # creating hls encrypted file for ad1 video
    ad1_hls = video_ad1.hls(Formats.h264())
    ad1_hls.encryption(save_to, url)
    ad1_hls.representations(_480p)
    ad1_hls.output(os.path.join(path_transform + '\hls_ad1.m3u8'))

    # creating hls encrypted file for ad2 video
    ad2_hls = video_ad2.hls(Formats.h264())
    ad2_hls.encryption(save_to, url)
    ad2_hls.representations(_480p)
    ad2_hls.output(os.path.join(path_transform + '\hls_ad2.m3u8'))
    atexit.register(print, "HLS encryption for all videos successful with encryption key generation")

if __name__ == "__main__":
    start_time = time.time()
    video_to_hls()
    hls_enc()
    print("--- %s seconds ---" % (time.time() - start_time))