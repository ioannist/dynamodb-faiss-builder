import json
import os
from pathlib import Path
from shutil import copyfile
import boto3
import botocore
from botocore.exceptions import ClientError
botocore.__version__

aws_access_key = 'AKIAXPFYXPRTLKFBZTOU'
aws_secret_key = '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'
s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                  aws_secret_access_key=aws_secret_key)
s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key,
                             aws_secret_access_key=aws_secret_key)

bucket = "<MY BUCKET>"


class S3App:

    def __init__(self, content_group):
        self.content_group = content_group

    # downloads and returns the serialized faiss index for this content_group
    def download_sentence_transformers(self):
        print(f"Downloading sentence_transformers")
        key = f"ml/libs/python/sentence_transformers_038.zip"
        file_path = "/mnt/efs/tmp/sentence_transformers.zip"
        Path("/mnt/efs/tmp/").mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            try:
                s3.download_fileobj(bucket, key, f)
                print("File downloaded")
            except botocore.exceptions.ClientError as err:
                print(err)
                raise err
        return file_path

    def download_distilbert(self):
        print(f"Downloading distilbert model")
        key = f"ml/models/distilbert_base_nli_stsb_mean_tokens/distilbert-base-nli-stsb-mean-tokens.zip"
        file_path = "/mnt/efs/tmp/distilbert_base_nli_stsb_mean_tokens.zip"
        Path("/mnt/efs/tmp/").mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            s3.download_fileobj(bucket, key, f)
            print("File downloaded")
        return file_path

