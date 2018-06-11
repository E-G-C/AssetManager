import json
import urllib
import boto3
import os
import shutil
import base64
import time
import pydevd

FOLDER_PREFIX = 'json-data'

# LOCAL_FOLDER = '/tmp'
LOCAL_FOLDER = 'c:\\work\\ML\\Homework\\tmp\\'
cognito_identity = '123456'


def lambda_handler(event, context):
    pydevd.settrace('192.168.50.100', port=53270, stdoutToServer=True, stderrToServer=True)

    request_body_json = json.loads(event['body'])

    file_name = request_body_json['file_name']
    file_content_base64 = request_body_json['file_content']

    file_content_byte_array = bytearray(file_content_base64)
    result = None

    s3 = boto3.resource('s3')
    epoch_time = int(time.time())
    custom_prefix = 'asset'
    file_key = f'{epoch_time}/{event["file_name"]}'

    bucket_name = f'{custom_prefix}-{cognito_identity}'
    bucket = s3.Bucket(bucket_name)
    bucket.create('private')
    bucket.put_object(Body=file_content_byte_array, Key=file_key)
    result = get_aws_api_response(200)
    return result


def get_cors_response():
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": 'true',
            'Content-Type': 'text/html',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
    }


def get_aws_api_response(status_code, response_body=None):
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body.__dict__) if response_body else json.dumps({}),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": 'true',
            'Content-Type': 'application/json',
        },
    }

# filepath = 'c:\\work\ML\\Homework\\tmp\\myfile.txt'
# with open(filepath, 'rb') as f: s = f.read()
#
# event = {'file_name': 'myFile.txt', 'body': s}
# print(s)
# lambda_handler(event,None)
