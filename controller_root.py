from flask import Flask, request
import json


app = Flask(__name__)

'''
 Inserts ad in the video.
'''
@app.route('/case2',methods = ['POST', 'GET'])
def mp_hls():
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
		return "Video URI is None"
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



if __name__ == '__main__':
	app.run()
