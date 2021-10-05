import requests

from flask import flash
from flask import url_for
from flask import session

from urllib.parse import urlencode


class FB:
    
    def __init__(self, app, *args, **kwargs):

        self.app = app
        
        self.facebook_client_id = app.config.get('FACEBOOK_CLIENT_ID')
        self.facebook_client_secret = app.config.get('FACEBOOK_CLIENT_SECRET')
        
        self.domain = app.config.get('DOMAIN')
        self.aws_nlb = app.config.get('AWS_NLB')

        self.app.config['FACEBOOK'] = self
        
        self.log(f"FB initiated: {self}")
        
    
    def log(self, message):
        self.app.logger.info(message)
        
    
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

        self.log(f"AUTH autorization_url: {autorization_url}")
        
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
    
        picture = me_response_json.get('picture')
        picture_data = picture.get('data') if picture else ""
        picture_url = picture_data.get('url') if picture_data else ""
        
        session['name'] = me_response_json.get('name')
        session['email'] = me_response_json.get('email')
        session['username'] = me_response_json.get('short_name')
        session['picture_url'] = picture_url
        
        # self.log(f"CLAIMS me_endpoint: {me_endpoint}")
        # self.log(f"CLAIMS parameters: {parameters}")
        # self.log(f"CLAIMS me_response_json: {me_response_json}")
            
        login_referer = session['login_referer']
        session.pop('login_referer', None)
        
        self.app.users.populate_facebook_user()
            
        flash(f"Welcome, facebook user {session['username']}!", category='warning')
        
        return login_referer
    
    