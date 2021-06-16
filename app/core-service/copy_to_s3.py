import mimetypes

import os
import boto3


BUCKET_NAME = "m1-assets-test"
DIRECTORY_PATH = "/home/ec2-user/environment/m1/app"
DIRECTORY = "core-service"


s3_resource = boto3.resource("s3")

s3_resource.create_bucket(Bucket=BUCKET_NAME)

bucket = s3_resource.Bucket(BUCKET_NAME)
bucket.objects.all().delete()

def write_to_s3(bucket_name: str, from_file: str, to_file: str, mimetype) -> None:

    s3_resource.Bucket(bucket_name).upload_file(
        from_file, to_file, ExtraArgs={"ACL": "public-read", "ContentType": mimetype}
    )


def get_mimetype(file):
    mimetype, _ = mimetypes.guess_type(file)
    if mimetype is None:
        raise Exception("Failed to guess mimetype")
    return mimetype


def copy_to_s3():
    
    os.chdir(DIRECTORY_PATH)
    print("Load from:", os.getcwd())
    print("Assets:", os.listdir())
    
    for root, dirs, files in os.walk(DIRECTORY):
        if files:
            
            current_folder = root.replace(DIRECTORY + "/", "").replace(DIRECTORY, "")
            
            print(root + ":")

            for file in files:
                
                from_path = f"{root}/{file}"
                to_path = f"{current_folder}/{file}" if current_folder else file
                
                print("    ", from_path, "->", to_path)
                
                mimetype = get_mimetype(file)
                
                write_to_s3(BUCKET_NAME, from_path, to_path, mimetype)


if __name__ == "__main__":
    
    copy_to_s3()