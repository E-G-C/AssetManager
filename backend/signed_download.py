import boto3
import json
import os


class ResponseItem:
    success = False
    url = None

    def __init__(self, success: bool = False, url: str = None, message: str = None):
        self.success = success
        self.url = url
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


def get_download_url(file_id, cognito_username):
    try:
        custom_prefix = os.environ['PREFIX']

        bucket_name = f'{custom_prefix}-{cognito_username}'
        s3_client = boto3.client('s3')

        s3_call_arguments = {'Bucket': bucket_name, 'Prefix': file_id}

        s3_object_response = s3_client.list_objects_v2(**s3_call_arguments)

        file_key = s3_object_response['Contents'][0]['Key']
        print(file_key)

        download_url = s3_client.generate_presigned_url(
            ExpiresIn=60,
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key
            }
        )
        result = {'success': True, 'url': download_url}
    except Exception as ex:
        exception_details = f'{type(ex)} {str(ex)}'
        result = {'success': False, 'message': exception_details}
    return result


def lambda_handler(event, context):
    result = None

    if event['requestContext'].get('authorizer', ''):
        if (event is not None) and ('queryStringParameters' in event) and (
                event['queryStringParameters'] is not None) and (
                event['queryStringParameters'].get('file_id', '')):
            file_id = event['queryStringParameters'].get('file_id', '')
            cognito_username = event['requestContext']['authorizer']['claims']['cognito:username']
            result = get_download_url(file_id=file_id, cognito_username=cognito_username)
        else:
            result = {'success': False, 'message': 'missing file_name parameter'}

    else:
        result = {'success': False, 'message': 'unknown user'}
    return get_aws_api_response(response_body=result)
