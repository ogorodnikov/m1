import os
import boto3
from dotenv import load_dotenv

load_dotenv()

print(os.getenv('DEFAULT_REGION'))


username = 'test'
password = '123456'
client_id = '19a0cvebjtej10gesr5r94qfqv'

client = boto3.client('cognito-idp')

response = client.initiate_auth(
    ClientId=client_id,
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': username,
        'PASSWORD': password
    }
)

print(response)


### New password required

# session = response['Session']
# 
# print(session)
# 
# response = client.respond_to_auth_challenge(
#     ClientId=client_id,
#     ChallengeName='NEW_PASSWORD_REQUIRED',
#     Session=session,
#     ChallengeResponses={'USERNAME': username,         
#                         'NEW_PASSWORD': password})

print()
print()
print()

access_token = response['AuthenticationResult']['AccessToken']
refresh_token = response['AuthenticationResult']['RefreshToken']

print('AccessToken:', access_token)
print()

print('RefreshToken:', refresh_token)



response = client.get_user(AccessToken=access_token)

print()
print(response)

user_attributes = response['UserAttributes']
user_sub = next(attribute['Value'] for attribute in user_attributes
                if attribute['Name'] == 'sub')

print('User sub:', user_sub)