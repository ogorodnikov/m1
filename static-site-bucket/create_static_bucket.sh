#!/bin/sh

aws s3 ls

#aws s3 website s3://www.ogoro.me --index-document index.html

#aws s3api put-bucket-policy --bucket www.ogoro.me --policy file://~/environment/m1/static-site-bucket/static-site-bucket-policy.json

#aws s3 sync ~/environment/m1/static-site-bucket/S3 s3://www.ogoro.me --delete