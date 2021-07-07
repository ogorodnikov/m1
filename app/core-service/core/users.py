import boto3
import botocore.exceptions

from core import app

from flask import session

user_pool_id = app.config.get('AWS_COGNITO_USER_POOL_ID')
client_id = app.config.get('AWS_COGNITO_USER_POOL_CLIENT_ID')

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
    
    
def link_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    provider = cognito_client.describe_identity_provider(UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'],
                                                         ProviderName='Facebook')
                                                         
    providers = cognito_client.list_identity_providers(UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'])
    
    
    link_result = cognito_client.admin_link_provider_for_user(
        
        UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'],
    
            DestinationUser={
                'ProviderName': 'Cognito',
                # 'ProviderAttributeName': 'string',
                'ProviderAttributeValue': username
            },
            SourceUser={
                'ProviderName': 'Facebook',
                'ProviderAttributeName': 'Cognito_Subject',
                'ProviderAttributeValue': '4041300779272291'
            }
        )
    

    register_response = {'status': link_result}
    
    return register_response
    
    


def facebook(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    app_id = '355403372591689'
    redirect_uri='https://ogoro.me'
    
    facebook_authorization_endpoint = f'https://www.facebook.com/v8.0/dialog/oauth?' + \
                                      f'client_id={app_id}&redirect_uri={redirect_uri}'
                                      
    # https://www.facebook.com/v8.0/dialog/oauth?client_id=355403372591689&redirect_uri=https://ogoro.me
        
    
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