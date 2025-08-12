import boto3
import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)

# Replace with your AWS credentials and bucket details
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = 'without-bulkboto'
local_folder_path = './test_dir' # e.g., 'C:/Users/YourUser/Documents/MyFiles' or '/home/user/my_files'
ENDPOINT_URL = "http://127.0.0.1:9000"

import re

def validate_string(input_string):
    """
    Validates a string against the regex ^[a-zA-Z0-9.\-_]{1,255}$.

    Args:
        input_string (str): The string to validate.

    Returns:
        bool: True if the string matches the regex, False otherwise.
    """
    regex_pattern = r"^[a-zA-Z0-9.\-_]{1,255}$"
    if re.fullmatch(regex_pattern, input_string):
        return True
    else:
        return False

def upload_folder_to_s3(local_folder, bucket):
    

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=ENDPOINT_URL
    )
    try:
        if not validate_string(bucket):
            raise ValueError(f"Invalid bucket name: {bucket}. Must match regex ^[a-zA-Z0-9.\-_]{1,255}$")
        s3.create_bucket(Bucket=bucket)
        print(f"Bucket '{bucket}' created successfully.")
    except Exception as e:
        print(f"Error creating bucket '{bucket_name}': {e}")
        
    for root, _, files in os.walk(local_folder):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            # Create S3 key relative to the local_folder_path
            #s3_key = os.path.relpath(local_file_path, local_folder).replace(os.sep, '/')
            s3_key = local_file_path.replace(local_folder, '').replace(os.sep, '/')
            s3_key = "".join(['/my-app/my-models/', s3_key])
            print(f"Uploading {local_file_path} to {bucket}{s3_key}")
            
            try:
                s3.upload_file(local_file_path, bucket, s3_key)
                print(f"Uploaded {local_file_path} to s3://{bucket}{s3_key}")
            except Exception as e:
                print(f"Error uploading {local_file_path}: {e}")

# Call the function to upload
upload_folder_to_s3(local_folder_path, bucket_name)