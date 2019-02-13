import json
import urllib2
import os
import base64
import shutil
from urllib2 import urlopen, URLError, HTTPError
import boto3
import zipfile
import requests

def upload_directory(src_dir, bucket_name, dst_dir):
    s3_resource = boto3.resource('s3', region_name=event['ResourceProperties']['Region'])
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.all().delete()
	
    if not os.path.isdir(src_dir):
        raise ValueError('src_dir %r not found.' % src_dir)
    all_files = []

    for root, dirs, files in os.walk(src_dir):
        all_files += [os.path.join(root, f) for f in files]
    

    for filename in all_files:
        s3_resource.Object(bucket_name, os.path.join(dst_dir, os.path.relpath(filename, src_dir)))\
            .put(Body=open(filename, 'rb'))
				
	
def handler(event, context):
    os.chdir('/tmp')
    if os.path.exists('/tmp/repo') and os.path.isdir('/tmp/repo'):
      shutil.rmtree('/tmp/repo')
    filename = os.path.join(os.getcwd(), 'repos.zip')
    url = event['repo_url']+"/zipball/master"

    r = requests.get(url)

    with open(filename, 'wb') as f:
      f.write(r.content)
    # unzip
    zip_ref = zipfile.ZipFile("repos.zip", 'r')
    zip_ref.extractall('/tmp/repo')
    zip_ref.close()
    # should only be one directory under repo
    files=os.listdir('/tmp/repo')
    repo=None
    for file in files:
      if file != '.' and file != '..':
        repo=file
	 
				
    upload_directory("/tmp/repo/"+repo, event['temp_bucket'], '')

		
event={}
context={}
event['temp_bucket']="jherbage-test"
event['repo_url']="https://github.com/jherbage/cloudformation-templates"
event['ResourceProperties']={}
event['ResourceProperties']['Region'] = 'eu-west-2'
handler(event,context)