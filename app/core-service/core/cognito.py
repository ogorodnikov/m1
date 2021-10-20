import os
import random

import boto3
import botocore.exceptions

from logging import getLogger


class Users:
    
    def __init__(self, *args, **kwargs):
        
        self.cognito_client = boto3.client('cognito-idp')
        
        self.logger = getLogger(__name__)
        
        self.domain = os.getenv('DOMAIN')
        self.aws_nlb = os.getenv('AWS_NLB')
        
        self.user_pool = os.getenv('USER_POOL')
        self.user_pool_client = os.getenv('USER_POOL_CLIENT')
        
        self.user_pool_id = self.get_user_pool_id(self.user_pool)
        self.client_id = self.get_client_id(self.user_pool_id, self.user_pool_client)

        self.log(f"COGNITO initiated: {self}")
        
    
    def log(self, message):
        
        self.logger.info(message)

        
    def get_user_pool_id(self, user_pool):

        user_pool_response = self.cognito_client.list_user_pools(MaxResults=60)
        user_pools = user_pool_response['UserPools']
        user_pool_id = next(attribute['Id'] for attribute in user_pools
                            if attribute['Name'] == user_pool)
                            
        return user_pool_id
    

    def get_client_id(self, user_pool_id, user_pool_client):
    
        user_pool_clients_response = self.cognito_client.list_user_pool_clients(UserPoolId=user_pool_id,
                                                                   MaxResults=60)
        user_pool_clients = user_pool_clients_response['UserPoolClients']
        user_pool_client_id = next(attribute['ClientId'] for attribute in user_pool_clients
                                   if attribute['ClientName'] == user_pool_client)
                            
        return user_pool_client_id


    def login_user(self, login_form):
        
        print(f"COGNITO login_form: {login_form}")
        
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
                                                             
    
        
        
        