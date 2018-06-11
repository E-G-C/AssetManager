import boto3
import time
import json
import os


class S3Object:
    # file_name = None
    # file_id = None
    # size = None

    def __init__(self, file_name: str = False, file_id: str = None, size: str = None):
        self.file_name = file_name
        self.file_id = file_id
        self.size = size


def get_aws_api_response(status_code=200, response_body=None):
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body) if response_body else json.dumps({}),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": 'true',
            'Content-Type': 'application/json'
        }

    }


def get_bucket_ls(cognito_username):
    result = None

    try:

        custom_prefix = os.environ['PREFIX']

        serialized_payload = '[]'
        s3_client = boto3.client('s3')

        bucket_name = f'{custom_prefix}-{cognito_username}'

        s3_objects = s3_client.list_objects_v2(Bucket=bucket_name)
        s3_objects_wrapper = []
        if s3_objects.get('Contents', ''):
            for s3_object in s3_objects['Contents']:
                s3_object_wrapper = S3Object(file_name=s3_object['Key'].split('/')[-1],
                                             file_id=s3_object['Key'].split('/')[0],
                                             size=s3_object['Size'])
                s3_objects_wrapper.append(s3_object_wrapper)

            serialized_payload = json.dumps([ob.__dict__ for ob in s3_objects_wrapper])
        result = {'success': True, 'payload': serialized_payload}

    except Exception as ex:
        exception_details = f'{type(ex)} {str(ex)}'
        result = {'success': False, 'message': exception_details}

    return result


def lambda_handler(event, context):
    result = None

    if event['requestContext'].get('authorizer', ''):
        cognito_username = event['requestContext']['authorizer']['claims']['cognito:username']
        result = get_bucket_ls(cognito_username=cognito_username)

    else:
        result = {'success': False, 'message': 'unknown user'}

    return get_aws_api_response(status_code=200, response_body=result)
