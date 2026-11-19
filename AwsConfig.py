import boto3


def s3_connect():
    return boto3.client(
        service_name='s3',
        region_name='ap-south-1',
        aws_access_key_id='AKIAQJBY262URAQOZIF2',
        aws_secret_access_key='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'
    )


class AwsConfig:
    def __init__(self):
        pass