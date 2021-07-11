from flask import flash, session, url_for

import boto3
import botocore.exceptions

from core import app


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
        
        app.logger.info(f'LOGIN token_response: {token_response}')
        app.logger.info(f'LOGIN access_token: {access_token}')
        app.logger.info(f'LOGIN refresh_token: {refresh_token}')
        app.logger.info(f'LOGIN user_response: {user_response}')
        app.logger.info(f'LOGIN user_attributes: {user_attributes}')
        app.logger.info(f'LOGIN user_sub: {user_sub}')

        session.permanent = login_form.get('remember_me')
            
        session['username'] = username
        
        flash(f"Welcome, {session['username']}!", category='warning')
    
    except Exception as exception:
        
        flash(f"Login did not pass... {exception}", category='danger')
    
    login_referer = session['login_referer']
    session.pop('login_referer', None)
            
    return login_referer
    
    
    
def register_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    try:
        
        app.logger.info(f'REGISTER login_form: {login_form}')
    
        sign_up_response = cognito_client.sign_up(ClientId=client_id,
                                                   Username=username,
                                                   Password=password)
        
        # confirmation_response = cognito_client.confirm_sign_up(ClientId=client_id,
        #                                                       Username=username,
        #                                                       ConfirmationCode='')
        
        confirmation_response = cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id,
                                                                     Username=username)
                                                                     
        app.logger.info(f'REGISTER client_id: {client_id}')
        app.logger.info(f'REGISTER user_pool_id: {user_pool_id}')
        app.logger.info(f'REGISTER sign_up_response: {sign_up_response}')
        app.logger.info(f'REGISTER confirmation_response: {confirmation_response}')
        
        flash(f"New user registered", category='info')
            
        redirect_to_sign_in_args = login_form.copy()
        redirect_to_sign_in_args['flow'] = 'sign-in'
        
        return url_for('login', **redirect_to_sign_in_args)
        
    except Exception as exception:
        
        flash(f"Registration did not pass... {exception}", category='danger')
    
        login_referer = session['login_referer']
        session.pop('login_referer', None)
            
        return login_referer
