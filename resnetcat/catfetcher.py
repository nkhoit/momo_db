import os
import PIL
from PIL import Image
import json
import boto3
import requests
from io import BytesIO
import urllib.parse

s3client = boto3.client('s3')

def getFilenamesFromUrls(urls):
    return list(map(lambda url : url[url.rindex('/')+1:], urls))

def sanitizeStrings(x):
	return list(map(lambda z : urllib.parse.quote(z), x))

def buildUrl(key):
  return "https://s3.amazonaws.com/www.momobot.net/%s" % key;

def getFilenames(pfx):
  response = s3client.list_objects(Bucket='www.momobot.net', Prefix=pfx);
  return list(filter(lambda l : l[-1] != '/',map(lambda l : l['Key'], response['Contents'])));

#They include the "mimo/" bucket prefix, so these need to be chopped to get filenames
mimoPrefixes = getFilenames('mimo')
mimosUrls = list(map(lambda l : buildUrl(l), mimoPrefixes));
mimos = list(map(lambda l : l[5:], mimoPrefixes));

momoPrefixes = getFilenames('momo')
momosUrls = list(map(lambda l : buildUrl(l), momoPrefixes));
momos = list(map(lambda l : l[5:], momoPrefixes));

mimiPrefixes = getFilenames('mimi')
mimisUrls = list(map(lambda l : buildUrl(l), mimiPrefixes));
mimis = list(map(lambda l : l[5:], mimiPrefixes));

#input drectory of images to compress
dirin1 = "./"
#dirin2list = ["cat", "cat2", "cats"]
dirin2list = ["momo", "mimi", "mimo"]
urlslist = [momosUrls, mimisUrls, mimosUrls]
filenamesList = [momos, mimis, mimos]
for i in range(len(dirin2list)):
	dirin2 = dirin2list[i];
	urls = urlslist[i];
	filenames = filenamesList[i];
	#create a directory to store compressed images
	dirout = dirin1 + "compressed" + dirin2
	
	try:
		os.stat(dirout)
	except:
		os.mkdir(dirout)
	
	#size of thumbnail
	size = 224, 224
	
	localFiles = list(filter(lambda i : i[-5:] != ".json", os.listdir(dirout)))
	remoteFiles = getFilenamesFromUrls(urls)
	extras = list(set(localFiles).difference(set(remoteFiles)))
	for fileName in extras:
		fullPath = dirout + "/" + fileName
		print("deleted: " + fullPath)
		os.remove(fullPath)
	for i in range(len(urls)):
		filename = filenames[i];
		url = urls[i];
		fout = dirout + "/" + filename
		if (os.path.isfile(fout)):
			continue;
		print("Adding picture: " + fout)
		response = requests.get(url)
		im = Image.open(BytesIO(response.content))
		im2 = im.resize(size, PIL.Image.LANCZOS)
		im2.save(fout, optimize = True)
