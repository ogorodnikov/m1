import random

from flask import flash
from flask import url_for
from flask import session
from flask import redirect

import boto3
import botocore.exceptions


class Users:
    
    def __init__(self, app, *args, **kwargs):

        self.cognito_client = boto3.client('cognito-idp')
        
        self.app = app

        self.client_id = app.config.get('COGNITO_USER_POOL_CLIENT_ID')        
        self.user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
        
        self.domain = app.config.get('DOMAIN')
        self.aws_nlb = app.config.get('AWS_NLB')
        
        app.users = self

        # self.log(f"COGNITO self.client_id: {self.client_id}")
        # self.log(f"COGNITO self.user_pool_id: {self.user_pool_id}")
        
        # self.log(f"COGNITO self.domain: {self.domain}")
        # self.log(f"COGNITO self.aws_nlb: {self.aws_nlb}")

        self.log(f"COGNITO initiated: {app.users}")
        
    
    def log(self, message):
        self.app.logger.info(message)


    def login_user(self, login_form):
        
        username = login_form.get('username')
        password = login_form.get('password')
        email = login_form.get('email')
        
        self.log(f'LOGIN Username: {username}')
        
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
        
        # self.log(f'LOGIN token_response: {token_response}')
        # self.log(f'LOGIN access_token: {access_token}')
        # self.log(f'LOGIN refresh_token: {refresh_token}')
        # self.log(f'LOGIN user_response: {user_response}')
        # self.log(f'LOGIN user_attributes: {user_attributes}')
        # self.log(f'LOGIN user_sub: {user_sub}')

        return username
        

    def register_user(self, login_form):
        
        username = login_form.get('username')
        password = login_form.get('password')

        self.log(f'REGISTER Username: {username}')
    
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

        
    def populate_facebook_user(self, name, email, full_name, picture_url):
        
        self.log(f'POPULATE User: {email}')
        
        user_response = self.cognito_client.list_users(
            UserPoolId=self.user_pool_id,
            Filter=f"email=\"{email}\""
        )
        
        user_already_in_cognito = bool(user_response['Users'])
        
        # self.log(f'POPULATE user_response: {user_response}')
        # self.log(f'POPULATE user_already_in_cognito: {user_already_in_cognito}')
        
        if user_already_in_cognito:
            
            self.log(f'POPULATE User is already in Cognito: {email}')
            return
        
        fb_username = 'fb_' + email.replace('@', '_')
        
        random_password = str(random.randint(0, 1000000))
        
        self.cognito_client.sign_up(
            ClientId=self.client_id,
            Username=fb_username,
            Password=random_password,
            UserAttributes=[
                {'Name': 'name', 
                 'Value': name},
                {'Name': 'email', 
                 'Value': email},
                {'Name': 'custom:full_name', 
                 'Value': full_name},
                {'Name': 'custom:picture_url', 
                 'Value': picture_url}
            ]
        )
        
        self.cognito_client.admin_confirm_sign_up(
            UserPoolId=self.user_pool_id,
            Username=fb_username
        )
                                             
        self.log(f'POPULATE Successful: {fb_username}')    
                                                             
    
        
        
        