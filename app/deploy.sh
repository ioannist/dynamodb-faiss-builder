#!/bin/bash
_function="DynamoFaissBuilder"
_s3_bucket="my_bucket"
echo $_function
virtualenv myvenv &&
source myvenv/bin/activate &&
# pip install -r requirements.txt --target ./package requests &&
pip install -r requirements.txt &&
deactivate &&
cd myvenv/lib/python3.7/site-packages &&
zip -r lambda.zip . &&
cd /app &&
zip -u myvenv/lib/python3.7/site-packages/lambda.zip main.py faiss_app.py s3_app.py dynamo_app.py &&
aws s3 cp "myvenv/lib/python3.7/site-packages/lambda.zip" s3://$_s3_bucket/cache/$_function.python.zip &&
aws lambda update-function-code --function-name $_function --s3-bucket $_s3_bucket --s3-key cache/$_function.python.zip &&
exit