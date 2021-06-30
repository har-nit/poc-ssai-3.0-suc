import re
import subprocess
from pathlib import Path
import time
import os

home = str(Path.home())

#change the location of file root
root = os.path.join(home, "Desktop", "AdInsertion")
if not os.path.exists(root):
    os.makedirs(root)
    print("Root folder created")
else:
    print("Root folder already exists")

path_transform = os.path.join(home, "Desktop", "AdInsertion", "Converted")
if not os.path.exists(path_transform):
    os.makedirs(path_transform)
    print("Converted folder created")

out_main = os.path.join("\converted", "output_main_file_480p.m3u8")
out_ad1 = os.path.join("\converted", "output_ad1_file_480p.m3u8")
out_ad2 = os.path.join("\converted", "output_ad2_file_480p.m3u8")

root_manifest = (os.path.join(root+out_main))
ad1_manifest = (os.path.join(root+out_ad1))
ad2_manifest = (os.path.join(root+out_ad2))

# ===========================   STEP:1
#### Reading the main file for EXTINF reading ####
# This function will read the main .m3u8 file and split the data into tags basis and it's time for cue point searching

def main_reader():
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
        (ext_main_list).insert((count * 2) + i +8 , ad2_list[i])

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

    with open(path_transform+r"\last_manifest.m3u8", 'w') as file_handler:
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

if __name__ == "__main__":
    main_reader()