import boto3

from core import app

from flask import session


client_id = app.config.get('AWS_COGNITO_USER_POOL_CLIENT_ID')

cognito_client = boto3.client('cognito-idp')


def login_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    token_response = cognito_client.initiate_auth(ClientId=client_id,
                                                  AuthFlow='USER_PASSWORD_AUTH',
                                                  AuthParameters={'USERNAME': username,
                                                                  'PASSWORD': password})
    
    access_token = token_response['AuthenticationResult']['AccessToken']
    refresh_token = token_response['AuthenticationResult']['RefreshToken']
    
    user_response = cognito_client.get_user(AccessToken=access_token)
    
    username = user_response['Username']
    
    user_attributes = user_response['UserAttributes']
    
    user_sub = next(attribute['Value'] for attribute in user_attributes
                    if attribute['Name'] == 'sub')    
    
    print('Token response:', token_response)
    print()
    print('AccessToken:', access_token)
    print()
    print('RefreshToken:', refresh_token)
    print()
    print('User response:', user_response)
    print()
    print('User attributes:', user_attributes)
    print()
    print('User sub:', user_sub)
        
    session['username'] = username
    
    login_response = {'status': 'logged-in'}
    
    return login_response
    
    
    
def register_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    sign_up_response = cognito_client.sign_up(ClientId=client_id,
                                               Username=username,
                                               Password=password)
    
    # access_token = token_response['AuthenticationResult']['AccessToken']
    # refresh_token = token_response['AuthenticationResult']['RefreshToken']
    
    # user_response = cognito_client.get_user(AccessToken=access_token)
    
    # username = user_response['Username']
    
    # user_attributes = user_response['UserAttributes']
    
    # user_sub = next(attribute['Value'] for attribute in user_attributes
    #                 if attribute['Name'] == 'sub')    
    
    print('Sign up response:', sign_up_response)
    print()
    # print('AccessToken:', access_token)
    # print()
    # print('RefreshToken:', refresh_token)
    # print()
    # print('User response:', user_response)
    # print()
    # print('User attributes:', user_attributes)
    # print()
    # print('User sub:', user_sub)
        
    # session['username'] = username
    
    register_response = {'status': 'registered'}
    
    return register_response