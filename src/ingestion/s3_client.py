from boto3 import client

def get_s3_client():
    """
    creates and returns an Amazon S3 client using the AWS credentials
    """
    return client("s3")