import os
import requests

from urllib.parse import urlencode

from logging import getLogger


class Facebook:
    
    def __init__(self):
        
        self.logger = getLogger(__name__)
        
        self.facebook_client_id = os.getenv('FACEBOOK_CLIENT_ID')
        self.facebook_client_secret = os.getenv('FACEBOOK_CLIENT_SECRET')
        
        self.domain = os.getenv('DOMAIN')
        self.aws_nlb = os.getenv('AWS_NLB')
        
        self.log(f"FB initiated: {self}")

    
    def log(self, message):
        self.logger.info(message)
        

    def replace_proxy(self, url):
        
        url_without_proxy = url.replace(self.aws_nlb, self.domain)
        
        return url_without_proxy
        

    def get_autorization_url(self, login_url):
        
        autorization_endpoint = 'https://www.facebook.com/v8.0/dialog/oauth'
        
        login_url_without_proxy = self.replace_proxy(login_url)
        
        parameters = {'client_id': self.facebook_client_id,
                      'redirect_uri': login_url_without_proxy,
                      'scope': 'public_profile,email'}
                      
        autorization_url = autorization_endpoint + '?' + urlencode(parameters)

        return autorization_url
        
    
    def get_token_from_code(self, code, login_url):
        
        token_endpoint = 'https://graph.facebook.com/oauth/access_token'
        
        login_url_without_proxy = self.replace_proxy(login_url)
        
        parameters = {'client_id': self.facebook_client_id,
                      'client_secret': self.facebook_client_secret,
                      'grant_type': 'authorization_code',
                      'redirect_uri': login_url_without_proxy,
                      'code': code}
                      
        access_token_url = token_endpoint + '?' + urlencode(parameters)
        
        # token_response = requests.get(token_endpoint, parameters)
        token_response = requests.get(access_token_url)
        
        token_response_json = token_response.json()
        facebook_token = token_response_json.get('access_token')
        
        # self.log(f"AUTH code: {code}")
        # self.log(f"TOKEN login_url_without_proxy: {login_url_without_proxy}")
        # self.log(f"TOKEN parameters: {parameters}")
        # self.log(f"TOKEN access_token_url: {access_token_url}")
        # self.log(f"TOKEN token_response: {token_response}")
        # self.log(f"TOKEN token_response_json: {token_response_json}")   
        # self.log(f"TOKEN facebook_token: {facebook_token}")
        
        return facebook_token
        
    
    def get_user_data(self, access_token):
                
        me_endpoint = 'https://graph.facebook.com/me'
        
        parameters = {'fields': 'name,email,picture,short_name',
                      'access_token': access_token}
                      
        me_response = requests.get(me_endpoint, parameters)
        me_response_json = me_response.json()
        
        # self.log(f"CLAIMS me_endpoint: {me_endpoint}")
        # self.log(f"CLAIMS parameters: {parameters}")
        # self.log(f"CLAIMS me_response_json: {me_response_json}")

        name = me_response_json.get('short_name')        
        email = me_response_json.get('email')
        full_name = me_response_json.get('name')
        
        error = me_response_json.get('error')
    
        picture = me_response_json.get('picture')
        picture_data = picture.get('data') if picture else {}
        picture_url = picture_data.get('url') if picture_data else ""
        
        user_data = {
            'name': name,
            'email': email,
            'full_name': full_name,
            'picture_url': picture_url,
            'error': error
        }

        self.log(f'FACEBOOK Login name: {name}')
        
        return user_data
    
    