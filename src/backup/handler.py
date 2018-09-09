import boto3
import json


def backup(event, context):

    client = boto3.client('ssm')
    value = client.get_parameter(Name='PRIVATE_KEY', WithDecryption=True)['Parameter']['Value']

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body),
        "secret": value
    }

    return response
