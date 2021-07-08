import boto3
import botocore.exceptions

from core import app

from flask import session

user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
client_id = app.config.get('COGNITO_USER_POOL_CLIENT_ID')

cognito_client = boto3.client('cognito-idp')


def login_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    try:
        
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
    
    except Exception as exception:
        
        login_response = {'status': repr(exception)}
        
    return login_response
    
    
    
def register_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    sign_up_response = cognito_client.sign_up(ClientId=client_id,
                                               Username=username,
                                               Password=password)
    
    # confirmation_response = cognito_client.confirm_sign_up(ClientId=client_id,
    #                                                       Username=username,
    #                                                       ConfirmationCode='')
    
    confirmation_response = cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id,
                                                                 Username=username)

    print('Sign up response:', sign_up_response)
    print()
    
    print('Confirmation response:', confirmation_response)
    print()
    
    register_response = {'status': 'registered'}
    
    return register_response
    
    
