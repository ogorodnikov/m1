from flask import flash, session, url_for, redirect

import boto3
import botocore.exceptions

from core import app


user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
client_id = app.config.get('COGNITO_USER_POOL_CLIENT_ID')

cognito_client = boto3.client('cognito-idp')


def login_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    email = login_form.get('email')
    
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
            
        redirect_to_sign_in_args = login_form.copy()
        redirect_to_sign_in_args['flow'] = 'sign-in'
        
        redirect_uri = url_for('login', _external=True, _scheme='https', **redirect_to_sign_in_args)
    
        aws_nlb = app.config['AWS_NLB']
        domain = app.config['DOMAIN']
        
        redirect_uri_after_proxy = redirect_uri.replace(aws_nlb, domain)
        
        app.logger.info(f'REGISTER client_id: {client_id}')
        app.logger.info(f'REGISTER user_pool_id: {user_pool_id}')
        app.logger.info(f'REGISTER sign_up_response: {sign_up_response}')
        app.logger.info(f'REGISTER confirmation_response: {confirmation_response}')
        app.logger.info(f'REGISTER redirect_to_sign_in_args: {redirect_to_sign_in_args}')
        app.logger.info(f'REGISTER redirect_uri: {redirect_uri}')
        app.logger.info(f'REGISTER redirect_uri_after_proxy: {redirect_uri_after_proxy}')
        
        flash(f"New user registered", category='info')
        
        return redirect_uri_after_proxy
        
    except Exception as exception:
        
        flash(f"Registration did not pass... {exception}", category='danger')
    
        login_referer = session['login_referer']
        session.pop('login_referer', None)
            
        return login_referer

    
def populate_facebook_user():
    
    user_response = cognito_client.list_users(UserPoolId=user_pool_id,
                                              Filter=f"email=\"{session['email']}\"")
    
    user_already_in_cognito = bool(user_response['Users'])
    
    app.logger.info(f'POPULATE user_response: {user_response}')
    app.logger.info(f'POPULATE user_already_in_cognito: {user_already_in_cognito}')
    
    if user_already_in_cognito:

        return
    
    fb_username = 'fb_' + session['email'].replace('@', '_')
    
    cognito_client.sign_up(ClientId=client_id,
                           Username=fb_username,
                           Password='11111111',
                           UserAttributes=[{'Name': 'name', 
                                            'Value': session['name']},
                                           {'Name': 'email', 
                                            'Value': session['email']},
                                           {'Name': 'custom:picture_url', 
                                            'Value': session['picture_url']}])
    
    cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id,
                                         Username=fb_username)
                                         
    app.logger.info(f'POPULATE session: {session}')
    app.logger.info(f'POPULATE fb_username: {fb_username}')    
    app.logger.info(f'POPULATE done')                                                                 

    
    
    