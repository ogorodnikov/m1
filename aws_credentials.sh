#!/bin/sh

AWS_ACCESS_KEY_ID=$(cat ~/.aws/credentials | grep -o -P '(?<=aws_access_key_id=).*')
AWS_SECRET_ACCESS_KEY=$(cat ~/.aws/credentials | grep -o -P '(?<=aws_secret_access_key=).*')
AWS_SESSION_TOKEN=$(cat ~/.aws/credentials | grep -o -P '(?<=aws_session_token=).*')
AWS_DEFAULT_REGION=$(cat ~/.aws/credentials | grep -o -P '(?<=region=).*')

echo 'export AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID
echo 'export AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY
echo 'export AWS_SESSION_TOKEN='$AWS_SESSION_TOKEN
echo 'export AWS_DEFAULT_REGION='$AWS_DEFAULT_REGION