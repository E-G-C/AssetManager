import boto3
import time
import json
import os


class ResponseItem:
    success = False
    url = None
    file_id = None
    message = None

    def __init__(self, success: bool = False, url: str = None, file_id: str = None, message: str = None):
        self.success = success
        self.url = url
        self.file_id = file_id
        self.message = message


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


def get_upload_url(file_name, cognito_username, expires_in=3600):
    # result = None

    try:

        custom_prefix = os.environ['PREFIX']

        s3_client = boto3.client('s3')

        epoch_time = int(time.time())
        file_key = f'{epoch_time}/{file_name}'

        bucket_name = f'{custom_prefix}-{cognito_username}'

        # # Make sure the folder exist # #
        s3_bucket = boto3.resource('s3').Bucket(bucket_name)
        s3_bucket.create('private')

        bucket_cors = s3_bucket.Cors()

        cors_config = {
            'CORSRules': [
                {
                    'AllowedMethods': ['GET', 'PUT'],
                    'AllowedOrigins': ['*'],
                    'AllowedHeaders': ['*']
                }
            ]
        }
        bucket_cors.put(CORSConfiguration=cors_config)

        # # # # # #-------------- # # # # #

        print('File Key: ' + file_key)
        print('Bucket Name:' + bucket_name)

        upload_url = s3_client.generate_presigned_url(
            ExpiresIn=expires_in,
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key,
                'ContentType': 'binary/octet-stream',
                'ACL': 'authenticated-read'}
        )
        # result = ResponseItem(success=True, url=upload_url, file_id=str(epoch_time))
        result = {'success': True, 'url': upload_url, 'file_id': str(epoch_time)}

    except Exception as ex:
        exception_details = f'{type(ex)} {str(ex)}'
        result = {'success': False, 'message': exception_details}

    return result


def lambda_handler(event, context):
    if event['requestContext'].get('authorizer', ''):
        if (event is not None) and ('queryStringParameters' in event) and (
                event['queryStringParameters'] is not None) and (
                event['queryStringParameters'].get('file_name', '')):
            file_name = event['queryStringParameters'].get('file_name', '')
            cognito_username = event['requestContext']['authorizer']['claims']['cognito:username']
            result = get_upload_url(file_name=file_name, cognito_username=cognito_username)
        else:
            result = {'success': False, 'message': 'missing file_name parameter'}

    else:
        result = {'success': False, 'message': 'unknown user'}

    # result = None
    #
    # if (event is not None) and ('queryStringParameters' in event) and (event['queryStringParameters'] is not None) and (
    #         event['queryStringParameters'].get('file_name', '')):
    #     file_name = event['queryStringParameters'].get('file_name', '')
    #     result = get_upload_url(file_name=file_name)
    # else:
    #     result = ResponseItem(success=False, message='file_name parameter is required')
    #
    return get_aws_api_response(response_body=result)
