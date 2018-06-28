import os
from PIL import Image
import json
import boto3
import requests
from io import BytesIO

s3client = boto3.client('s3')

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

treePrefixes = getFilenames('tree')
treeUrls = list(map(lambda l : buildUrl(l), treePrefixes));
trees = list(map(lambda l : l[5:], treePrefixes));

#input drectory of images to compress
dirin1 = "/var/www/"
#dirin2list = ["cat", "cat2", "cats"]
dirin2list = ["momo", "mimi", "mimo", "tree"]
urlslist = [momosUrls, mimisUrls, mimosUrls, treeUrls]
filenamesList = [momos, mimis, mimos, trees]
for i in range(len(dirin2list)):
	dirin2 = dirin2list[i];
	urls = urlslist[i];
	filenames = filenamesList[i];
	dirin3 = dirin1+dirin2
	#create a directory to store compressed images
	dirout = dirin1 + "compressed" + dirin2
	
	try:
		os.stat(dirout)
	except:
		os.mkdir(dirout)
	fins = os.listdir(dirin3)
	
	#size of thumbnail
	size = 100, 100
	
	diroutlist = dirout + "/" + "listing.json"
	listfile = open(diroutlist, mode='wt')
	json_str = json.dumps(filenames)
	listfile.write(json_str)
	listfile.close
	for i in range(len(urls)):
		filename = filenames[i];
		url = urls[i];
		fout = dirout + "/" + filename
		if (os.path.isfile(fout)):
			continue;
		response = requests.get(url)
		im = Image.open(BytesIO(response.content))
		im.thumbnail(size)
		im.save(fout, optimize = True)
