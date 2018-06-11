import boto3
import time
import json
import os


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


def delete_file(file_id, cognito_username):
    result = None

    try:
        custom_prefix = os.environ['PREFIX']
        s3_client = boto3.client('s3')

        bucket_name = f'{custom_prefix}-{cognito_username}'
        s3_call_arguments = {'Bucket': bucket_name, 'Prefix': str(file_id)}

        s3_objects = s3_client.list_objects_v2(**s3_call_arguments)

        file_key = s3_objects['Contents'][0]['Key']

        s3_client.delete_object(Bucket=bucket_name, Key=file_key)

        result = {'success': True, 'message': 'File deleted successfully'}

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
            result = delete_file(file_id=file_id, cognito_username=cognito_username)
        else:
            result = {'success': False, 'message': 'missing file_name parameter'}

    else:
        result = {'success': False, 'message': 'unknown user'}
    return get_aws_api_response(response_body=result)
