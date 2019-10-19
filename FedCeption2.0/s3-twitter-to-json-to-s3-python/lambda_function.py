# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import boto3
from botocore.exceptions import ClientError
import twitter_to_json
import time

s3 = boto3.client('s3')

def lambda_handler(event, context):
	print("Received event: " + json.dumps(event, indent=2))

	# Get the object from the event and show its content type
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']

	# Getting s3 object
	try:
		response = s3.get_object(Bucket=bucket, Key=key)
		
	except Exception as e:
		print(e)
		print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
		raise e
    
	# Parse s3 object content (JSON)
	try:
		s3_file_content = response['Body'].read()
		#clean trailing comma
		if s3_file_content.endswith(',\n'):
			s3_file_content = s3_file_content[:-2]
		tweets_str = '['+s3_file_content+']'
		tweets = json.loads(tweets_str)
   
	except Exception as e:
		print(e)
		print('Error loading json from object {} in bucket {}'.format(key, bucket))
		raise e
    
	tweets_as_json = json.dumps(twitter_to_json.load(tweets), ensure_ascii=False)
	print('object = {} ; bucket = {}'.format(key, bucket))

    # Put the object into the S3 bucket
	timestr = time.strftime("%Y%m%d-%H%M%S")
	dest_object_name = 'outputjsons/sentiment_analysis_' + timestr
	try:
		s3.put_object(Bucket=bucket, Key=dest_object_name, Body=tweets_as_json)
	except ClientError as e:
		# AllAccessDisabled error == bucket not found
		# NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
		print(e)
	finally:
		if isinstance(tweets_as_json, str):
			object_data.close()

if __name__ == '__main__':
	event = {
		'Records': [
			{
				's3': {
					'bucket': {
						'name': 'YOUR_BUCKET'
					},
					'object': {
						'key': 'YOUR_KEY'
					}
				}
			}
		]
	}
	lambda_handler(event, None)
