import os
import requests

from flask import flash
from flask import url_for
from flask import session

from urllib.parse import urlencode

from logging import getLogger


class FB:
    
    def __init__(self, users, *args, **kwargs):

        self.users = users
        
        self.logger = getLogger(__name__)
        
        self.facebook_client_id = os.getenv('FACEBOOK_CLIENT_ID')
        self.facebook_client_secret = os.getenv('FACEBOOK_CLIENT_SECRET')
        
        self.domain = os.getenv('DOMAIN')
        self.aws_nlb = os.getenv('AWS_NLB')
        
        self.log(f"FB initiated: {self}")

    
    def log(self, message):
        self.logger.info(message)
        
    
    @property
    def redirect_uri_after_proxy(self):
        
        redirect_uri = url_for('login', _external=True, _scheme='https')
    
        redirect_uri_after_proxy = redirect_uri.replace(self.aws_nlb, self.domain)
        
        # self.log(f"FB redirect_uri: {redirect_uri}")
        # self.log(f"FB redirect_uri_after_proxy: {redirect_uri_after_proxy}")
        
        return redirect_uri_after_proxy
        

    def get_autorization_url(self):
        
        autorization_endpoint = 'https://www.facebook.com/v8.0/dialog/oauth'
        
        parameters = {'client_id': self.facebook_client_id,
                      'redirect_uri': self.redirect_uri_after_proxy,
                      'scope': 'public_profile,email'}
                      
        autorization_url = autorization_endpoint + '?' + urlencode(parameters)

        # self.log(f"AUTH autorization_url: {autorization_url}")
        
        return autorization_url
        
    
    def code_to_token(self, code):
        
        token_endpoint = 'https://graph.facebook.com/oauth/access_token'
        
        parameters = {'client_id': self.facebook_client_id,
                      'client_secret': self.facebook_client_secret,
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.redirect_uri_after_proxy,
                      'code': code}
                      
        access_token_url = token_endpoint + '?' + urlencode(parameters)
        
        # token_response = requests.get(token_endpoint, parameters)
        token_response = requests.get(access_token_url)
        
        token_response_json = token_response.json()
        facebook_token = token_response_json.get('access_token')
        
        # self.log(f"AUTH code: {code}")
        # self.log(f"TOKEN self.redirect_uri_after_proxy: {self.redirect_uri_after_proxy}")
        # self.log(f"TOKEN parameters: {parameters}")
        # self.log(f"TOKEN access_token_url: {access_token_url}")
        # self.log(f"TOKEN token_response: {token_response}")
        # self.log(f"TOKEN token_response_json: {token_response_json}")   
        # self.log(f"TOKEN facebook_token: {facebook_token}")
        
        session['facebook_token'] = facebook_token    
        
        return facebook_token
        
    
    def login_facebook_user(self, access_token):
                
        me_endpoint = 'https://graph.facebook.com/me'
        
        parameters = {'fields': 'name,email,picture,short_name',
                      'access_token': access_token}
                      
        me_response = requests.get(me_endpoint, parameters)
        me_response_json = me_response.json()
        
        # self.log(f"CLAIMS me_endpoint: {me_endpoint}")
        # self.log(f"CLAIMS parameters: {parameters}")
        # self.log(f"CLAIMS me_response_json: {me_response_json}")
    
        picture = me_response_json.get('picture')
        picture_data = picture.get('data') if picture else ""
        picture_url = picture_data.get('url') if picture_data else ""
        
        name = me_response_json.get('short_name')        
        email = me_response_json.get('email')
        full_name = me_response_json.get('name')

        session['username'] = name
        session['email'] = email
        session['full_name'] = full_name
        session['picture_url'] = picture_url
            
        self.users.populate_facebook_user(name, email, full_name, picture_url)
        
        flash(f"Welcome, facebook user {name}!", category='warning')
        
        self.log(f'FACEBOOK Login successful: {name}')
        
        login_referer = session.pop('login_referer', None)
        
        return login_referer
    
    