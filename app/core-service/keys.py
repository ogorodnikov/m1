import json
import os
import requests


def get_cognito_public_keys():
    
    # region = os.environ["AWS_REGION"]
    # pool_id = os.environ["AWS_COGNITO_USER_POOL_ID"]
    # url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    
    # [print(key, ':', os.environ[key]) for key in os.environ]
    
    # url = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_eADXvMciJ/.well-known/jwks.json"
    # resp = requests.get(url)
    # print(resp)
    
    # print(json.dumps(json.loads(resp.text)["keys"][1]))
    
    print(os.environ["REGION"])
    
    
    
    
if __name__ == "__main__":
    
    get_cognito_public_keys()