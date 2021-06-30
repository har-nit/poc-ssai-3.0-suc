# imported the requests library
import requests
from pathlib import Path
import time


home = str(Path.home())

#change the location of file root
root = home + "\Desktop\AdInsertion\source"

video_url = "https://drive.google.com/u/0/uc?id=1ImopSD0Er-SNVY2AyLyL5rD15DJL6fh9&export=download"

# URL of the image to be downloaded is defined as image_url
r = requests.get(video_url) # create HTTP response object

# send a HTTP request to the server and save
# the HTTP response in a response object called r
with open(root+"/1.mp4",'wb') as f:
	f.write(r.content)
