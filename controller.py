from flask import Flask, request
import json
import requests
import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size
import json
import subprocess
import atexit
import re
import os
from pathlib import Path
import time

app = Flask(__name__)
'''
 Inserts ad in the video.
'''
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
print(video_main)

root_main = (os.path.join(root+out_main))
root_ad1 = (os.path.join(root+out_ad1))
root_ad2 = (os.path.join(root+out_ad2))
print(root_main)

root_manifest = (os.path.join(root_main+"_480p.m3u8"))
ad1_manifest = (os.path.join(root_ad1+"_480p.m3u8"))
ad2_manifest = (os.path.join(root_ad2+"_480p.m3u8"))
print(root_manifest)

@app.route('/case2',methods = ['POST', 'GET'])
def case2():
	data = json.loads(request.data)
	'''
	data object has request json
	'''
	validation_response = is_valid_requestJson(data)
	if validation_response is None:
		'''
		   If length is zero it means valid message proceed ahead for ad insertion
		   @Ishan please integrate your code here starting from downloading the m3u8 files from the urls and logic ahead of it
		'''

		#code to download video from the json request

		if data['videoUri'] is not None:
			video_url = data['videoUri']

			r = requests.get(video_url)  # create HTTP response object

			with open(path_source + "\main.mp4", 'wb') as f:
				f.write(r.content)
				print("main video downloaded")

		ads = data['ads']
		ads_list= []
		count = 1
		for obj in ads:
			ads_list.append(obj['adUri'])

		for i in ads_list:
			ad_count = len(obj)
			video_url = i
			r = requests.get(video_url)  # create HTTP response object
			name = "\{}.mp4".format(count)
			with open(path_source+name, 'wb') as f:
				f.write(r.content)
			count+= 1
			if count > ad_count:
				break
		print("ads videos downloaded")

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
		print("HLS files generation and generating encryption key in process...")

		# A path you want to save a random key to your local machine
		save_to = root + '/key'

		# A URL (or a path) to access the key on your website
		url = 'http://www.localhost.com/test2/key'
		# or url = '/"PATH TO THE KEY DIRECTORY"/key';

		# creating hls encrypted file for main video
		# main_hls = video_main.hls(Formats.h264())
		# main_hls.encryption(save_to, url)
		# main_hls.representations(_480p)
		# main_hls.output(os.path.join(path_transform + '\hls_main.m3u8'))
		# #
		# # # creating hls encrypted file for ad1 video
		# ad1_hls = video_ad1.hls(Formats.h264())
		# ad1_hls.encryption(save_to, url)
		# ad1_hls.representations(_480p)
		# ad1_hls.output(os.path.join(path_transform + '\hls_ad1.m3u8'))
		# #
		# # # creating hls encrypted file for ad2 video
		# ad2_hls = video_ad2.hls(Formats.h264())
		# ad2_hls.encryption(save_to, url)
		# ad2_hls.representations(_480p)
		# ad2_hls.output(os.path.join(path_transform + '\hls_ad2.m3u8'))
		atexit.register(print, "HLS encryption for all videos successful with encryption key generation")

		main_file = open(root_manifest, "r")
		main = main_file.readlines()

		main_extinf_list = []
		extinf_time_list = []
		for i in main:
			if 'EXTINF' in i:
				main_extinf_list.append(i)

		for i in range(len(main_extinf_list)):
			text = re.sub("[^\d\.]", "", main_extinf_list[i])
			extinf_time_list.append(text)
		# main_file.close()

		print("main", main)
		print("extinf_time_list", extinf_time_list)

		# ===========================   STEP:2
		#### Now splitting the EXT tags from EXTINF tags ####
		# This function will separate the normal EXT tags with the EXTINF tags so that we can get time data from it

		string1 = '#EXTINF'
		string2 = 'output_main_file'
		# setting flag and index to 0
		flag = 0
		index = 0

		ext_main_list = []

		# Loop through the file line by line
		for line in main:
			index += 1

			# checking string is present in line or not
			if string1 in line:
				ext_main_list.append(main[index - 1])

			if string2 in line:
				ext_main_list.append(main[index - 1])

		# closing text file
		#     main_file.close()
		# This will get the residual hashes apart from the EXTINF tags

		print("ext_main_list", ext_main_list)

		cue_1 = 120
		# float(input('Enter the time in seconds where you want to insert the ad: '))
		cue_2_1 = 180
		# float(input('Enter the time in seconds where you want to insert the ad: '))
		cue_2_2 = 240
		# float(input('Enter the time in seconds where you want to insert the ad: '))

		cue_list = [cue_1, cue_2_1, cue_2_2]
		print("cue_list", cue_list)

		# ===========================   STEP:3
		#### Fetching EXTINF from AD files ####
		# This function will store the EXTINF tags for ad1 and ad2 so that it can be added to main file based on cue points

		ad1 = open(ad1_manifest, 'r')
		count = 0
		ad1_list = []
		while True:
			count += 1
			# Get next line from file
			line = ad1.readline()
			ad1_list.append(line)
			# if line is empty
			# end of file is reached
			if not line:
				break

		ad1_list = (ad1_list[5:9])
		ad1_list.insert(len(ad1_list), '#EXT-X-DISCONTINUITY\n')
		ad1.close()
		print("ad1_list", ad1_list)

		ad2 = open(ad2_manifest, 'r')
		count = 0
		ad2_list = []
		while True:
			count += 1

			# Get next line from file
			line = ad2.readline()
			ad2_list.append(line)
			# if line is empty
			# end of file is reached
			if not line:
				break

		ad2_list = (ad2_list[5:7])
		ad2_list.insert(len(ad2_list), '#EXT-X-DISCONTINUITY\n')
		ad2.close()
		print("ad2_list", ad2_list)

		# ===========================   STEP:4
		#### Adding EXTINF from AD files to MAIN file ####
		# This functions will add the EXTINF tags for ad1 and ad2 into the main files based on the time calculation and closes cue point
		# to the input time given

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= cue_list[0]:
				break

		for i in range(len(ad1_list)):
			ext_main_list.insert((count * 2) + i, ad1_list[i])
		print("inserted ad1", ext_main_list)

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= float(cue_list[1]):
				break

		for i in range(len(ad2_list)):
			(ext_main_list).insert((count * 2) + i + 3, ad2_list[i])

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= float(cue_list[1]):
				break

		for i in range(len(ad2_list)):
			(ext_main_list).insert((count * 2) + i + 8, ad2_list[i])

		print("inserted ad2", ext_main_list)

		# ===========================   STEP:5
		#### Making the final MANIFEST file ####
		# This functions will stich the normal ext tags with the AD and MAIN EXTINF tags

		new_manifest = []

		for i in ext_main_list:
			new_manifest.append(i)
		new_manifest.append(main[-1])

		testing = os.path.join(home, "Desktop", "AdInsertion", "testing")
		if not os.path.exists(testing):
			os.makedirs(testing)
			print("Testing folder created")
		else:
			print("Testing folder already exists")

		with open(path_transform + r"\last_manifest.m3u8", 'w') as file_handler:
			file_handler.write(main[0])
			file_handler.write(main[1])
			file_handler.write(main[2])
			file_handler.write(main[3])
			file_handler.write(main[4])

			for item in new_manifest:
				file_handler.write("{}".format(item))

		input_file = os.path.join(path_transform, "last_manifest.m3u8")
		out_file = os.path.join(path_transform, "manifest_video.mp4")
		command = 'ffmpeg -i ' + input_file + ' ' + out_file
		subprocess.run(command)

		start_time = time.time()
		print("--- %s seconds ---" % (time.time() - start_time))

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
	else:
		return validation_response

'''
   Checks if valid json is present in request.
'''

def is_valid_requestJson(data):
	validationOutput = ""
	if data is None:
		return "data is None"
	elif 'videoUri' not in data or data['videoUri'] is None:
		return  "Video URI is None"
	elif 'ads' not in data or data['ads'] is None:
		return "Ads is Not Available for insertion"
	else:
		ads = data['ads']
		for obj in ads:
			if obj is None:
				return "No ads to insert"
			elif obj['adUri'] is None:
				return "Ad URI is None"
			elif obj['adInsertionPoints'] is None:
				return "Ad Insertion point is not available"


@app.route('/case1',methods = ['POST', 'GET'])
def case1():
	data = json.loads(request.data)
	'''
	    data object has request json
	'''
	validation_response = is_valid_requestJson(data)
	if validation_response is None:
		'''
		   If length is zero it means valid message proceed ahead for ad insertion
		   @Ishan please integrate your code here starting from downloading the m3u8 files from the urls and logic ahead of it
		'''

		hls_folder = os.path.join(home, "Desktop", "HLS")
		if not os.path.exists(hls_folder):
			os.makedirs(hls_folder)
			print("HLS Folder folder created")
		else:
			print("Hls Folder already exists")

		if data['videoUri'] is not None:
			video_url = data['videoUri']

			r = requests.get(video_url)  # create HTTP response object

			with open(hls_folder+'\output_main_file_480p.m3u8', 'wb') as f:
				f.write(r.content)
				print("main file downloaded")

		ads = data['ads']
		ads_list = []
		count = 1
		for obj in ads:
			ads_list.append(obj['adUri'])

		for i in ads_list:
			ad_count = len(obj)
			video_url = i
			r = requests.get(video_url)  # create HTTP response object
			name = "\output_ad{}_file_480p.m3u8".format(count)
			with open(hls_folder + name, 'wb') as f:
				f.write(r.content)
			count += 1
			if count > ad_count:
				break
		print("ads videos downloaded")

		main_file = open(hls_folder+'\output_main_file_480p.m3u8', "r")
		main = main_file.readlines()

		main_extinf_list = []
		extinf_time_list = []
		for i in main:
			if 'EXTINF' in i:
				main_extinf_list.append(i)

		for i in range(len(main_extinf_list)):
			text = re.sub("[^\d\.]", "", main_extinf_list[i])
			extinf_time_list.append(text)
		# main_file.close()

		print("main", main)
		print("extinf_time_list", extinf_time_list)

		# ===========================   STEP:2
		#### Now splitting the EXT tags from EXTINF tags ####
		# This function will separate the normal EXT tags with the EXTINF tags so that we can get time data from it

		string1 = '#EXTINF'
		string2 = 'output_main_file'
		# setting flag and index to 0
		flag = 0
		index = 0

		ext_main_list = []

		# Loop through the file line by line
		for line in main:
			index += 1

			# checking string is present in line or not
			if string1 in line:
				ext_main_list.append(main[index - 1])

			if string2 in line:
				ext_main_list.append(main[index - 1])

		# closing text file
		#     main_file.close()
		# This will get the residual hashes apart from the EXTINF tags

		print("ext_main_list", ext_main_list)

		cue_1 = 120
		# float(input('Enter the time in seconds where you want to insert the ad: '))
		cue_2_1 = 180
		# float(input('Enter the time in seconds where you want to insert the ad: '))
		cue_2_2 = 240
		# float(input('Enter the time in seconds where you want to insert the ad: '))

		cue_list = [cue_1, cue_2_1, cue_2_2]
		print("cue_list", cue_list)

		# ===========================   STEP:3
		#### Fetching EXTINF from AD files ####
		# This function will store the EXTINF tags for ad1 and ad2 so that it can be added to main file based on cue points

		ad1 = open(hls_folder+'/output_ad1_file_480p.m3u8', 'r')
		count = 0
		ad1_list = []
		while True:
			count += 1
			# Get next line from file
			line = ad1.readline()
			ad1_list.append(line)
			# if line is empty
			# end of file is reached
			if not line:
				break

		ad1_list = (ad1_list[5:9])
		ad1_list.insert(len(ad1_list), '#EXT-X-DISCONTINUITY\n')
		ad1.close()
		print("ad1_list", ad1_list)

		ad2 = open(hls_folder+'/output_ad2_file_480p.m3u8', 'r')
		count = 0
		ad2_list = []
		while True:
			count += 1

			# Get next line from file
			line = ad2.readline()
			ad2_list.append(line)
			# if line is empty
			# end of file is reached
			if not line:
				break

		ad2_list = (ad2_list[5:7])
		ad2_list.insert(len(ad2_list), '#EXT-X-DISCONTINUITY\n')
		ad2.close()
		print("ad2_list", ad2_list)

		# ===========================   STEP:4
		#### Adding EXTINF from AD files to MAIN file ####
		# This functions will add the EXTINF tags for ad1 and ad2 into the main files based on the time calculation and closes cue point
		# to the input time given

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= cue_list[0]:
				break

		for i in range(len(ad1_list)):
			ext_main_list.insert((count * 2) + i, ad1_list[i])
		print("inserted ad1", ext_main_list)

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= float(cue_list[1]):
				break

		for i in range(len(ad2_list)):
			(ext_main_list).insert((count * 2) + i + 3, ad2_list[i])

		total = 0
		count = 0
		for ele in range(0, len(list(extinf_time_list))):
			count += 1
			total = total + float(extinf_time_list[ele])
			if total >= float(cue_list[1]):
				break

		for i in range(len(ad2_list)):
			(ext_main_list).insert((count * 2) + i + 8, ad2_list[i])

		print("inserted ad2", ext_main_list)

		# ===========================   STEP:5
		#### Making the final MANIFEST file ####
		# This functions will stich the normal ext tags with the AD and MAIN EXTINF tags

		new_manifest = []

		for i in ext_main_list:
			new_manifest.append(i)
		new_manifest.append(main[-1])

		testing = os.path.join(home, "Desktop", "AdInsertion", "testing")
		if not os.path.exists(testing):
			os.makedirs(testing)
			print("Testing folder created")
		else:
			print("Testing folder already exists")

		with open(hls_folder + r"\last_manifest.m3u8", 'w') as file_handler:
			file_handler.write(main[0])
			file_handler.write(main[1])
			file_handler.write(main[2])
			file_handler.write(main[3])
			file_handler.write(main[4])

			for item in new_manifest:
				file_handler.write("{}".format(item))


		start_time = time.time()
		print("--- %s seconds ---" % (time.time() - start_time))
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
	else:
		return validation_response

if __name__ == '__main__':
	app.run()
