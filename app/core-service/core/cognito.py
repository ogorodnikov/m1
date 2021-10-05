from flask import flash
from flask import url_for
from flask import session
from flask import redirect

import boto3
import botocore.exceptions


class Users:
    
    def __init__(self, app, *args, **kwargs):

        self.app = app

        self.cognito_client = boto3.client('cognito-idp')

        self.client_id = app.config.get('COGNITO_USER_POOL_CLIENT_ID')        
        self.user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
        
        self.domain = app.config.get('DOMAIN')
        self.aws_nlb = app.config.get('AWS_NLB')

        self.log(f"COGNITO self.client_id: {self.client_id}")
        self.log(f"COGNITO self.user_pool_id: {self.user_pool_id}")
        
        self.log(f"COGNITO self.domain: {self.domain}")
        self.log(f"COGNITO self.aws_nlb: {self.aws_nlb}")
        
        self.app.config['USERS'] = self
        
        self.log(f"COGNITO initiated: {self}")
        
    
    def log(self, message):
        self.app.logger.info(message)


    def login_user(self, login_form):
        
        username = login_form.get('username')
        password = login_form.get('password')
        email = login_form.get('email')
        
        try:
            
            token_response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': username,
                                'PASSWORD': password}
            )
            
            access_token = token_response['AuthenticationResult']['AccessToken']
            refresh_token = token_response['AuthenticationResult']['RefreshToken']
            
            user_response = self.cognito_client.get_user(AccessToken=access_token)
            
            username = user_response['Username']
            
            user_attributes = user_response['UserAttributes']
            
            user_sub = next(attribute['Value'] for attribute in user_attributes
                            if attribute['Name'] == 'sub')    
            
            self.log(f'LOGIN token_response: {token_response}')
            self.log(f'LOGIN access_token: {access_token}')
            self.log(f'LOGIN refresh_token: {refresh_token}')
            self.log(f'LOGIN user_response: {user_response}')
            self.log(f'LOGIN user_attributes: {user_attributes}')
            self.log(f'LOGIN user_sub: {user_sub}')
    
            session.permanent = login_form.get('remember_me')
                
            session['username'] = username
            
            flash(f"Welcome, {session['username']}!", category='warning')
        
        except Exception as exception:
            
            flash(f"Login did not pass... {exception}", category='danger')
        
        login_referer = session['login_referer']
        session.pop('login_referer', None)
                
        return login_referer
        
        
    def register_user(self, login_form):
        
        username = login_form.get('username')
        password = login_form.get('password')
        
        try:
            
            self.log(f'REGISTER login_form: {login_form}')
        
            sign_up_response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password
            )
            
            # confirmation_response = self.cognito_client.confirm_sign_up(
            #     ClientId=self.client_id,
            #     Username=username,
            #     ConfirmationCode=''
            # )
            
            confirmation_response = self.cognito_client.admin_confirm_sign_up(
                UserPoolId=self.user_pool_id,
                Username=username
            )
                
            redirect_to_sign_in_args = login_form.copy()
            redirect_to_sign_in_args['flow'] = 'sign-in'
            
            redirect_uri = url_for('login', _external=True, _scheme='https', 
                                   **redirect_to_sign_in_args)
        
            redirect_uri_after_proxy = redirect_uri.replace(self.aws_nlb, self.domain)
            
            self.log(f'REGISTER self.client_id: {self.client_id}')
            self.log(f'REGISTER self.user_pool_id: {self.user_pool_id}')
            self.log(f'REGISTER sign_up_response: {sign_up_response}')
            self.log(f'REGISTER confirmation_response: {confirmation_response}')
            self.log(f'REGISTER redirect_to_sign_in_args: {redirect_to_sign_in_args}')
            self.log(f'REGISTER redirect_uri: {redirect_uri}')
            self.log(f'REGISTER redirect_uri_after_proxy: {redirect_uri_after_proxy}')
            
            flash(f"New user registered", category='info')
            
            return redirect_uri_after_proxy
            
        except Exception as exception:
            
            flash(f"Registration did not pass... {exception}", category='danger')
        
            login_referer = session['login_referer']
            session.pop('login_referer', None)
                
            return login_referer
    
        
    def populate_facebook_user(self):
        
        user_response = self.cognito_client.list_users(
            UserPoolId=self.user_pool_id,
            Filter=f"email=\"{session['email']}\""
        )
        
        user_already_in_cognito = bool(user_response['Users'])
        
        self.log(f'POPULATE user_response: {user_response}')
        self.log(f'POPULATE user_already_in_cognito: {user_already_in_cognito}')
        
        if user_already_in_cognito:
            return
        
        fb_username = 'fb_' + session['email'].replace('@', '_')
        
        self.cognito_client.sign_up(
            ClientId=self.client_id,
            Username=fb_username,
            Password='11111111',
            UserAttributes=[
                {'Name': 'name', 
                 'Value': session['name']},
                {'Name': 'email', 
                 'Value': session['email']},
                {'Name': 'custom:picture_url', 
                 'Value': session['picture_url']}
            ]
        )
        
        self.cognito_client.admin_confirm_sign_up(
            UserPoolId=self.user_pool_id,
            Username=fb_username
        )
                                             
        self.log(f'POPULATE session: {session}')
        self.log(f'POPULATE fb_username: {fb_username}')    
        self.log(f'POPULATE done')                                                                 
    
        
        
        