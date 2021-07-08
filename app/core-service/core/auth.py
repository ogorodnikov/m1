import requests

from core import app

from flask import url_for

from urllib.parse import urlencode


facebook_client_id = app.config.get('FACEBOOK_CLIENT_ID')
facebook_client_secret = app.config.get('FACEBOOK_CLIENT_SECRET')


def get_autorization_url():
    
    autorization_endpoint = 'https://www.facebook.com/v8.0/dialog/oauth'
    
    redirect_uri = url_for('login', _external=True, _scheme='https')
    
    aws_nlb = app.config['AWS_NLB']
    domain = app.config['DOMAIN']
    redirect_uri_after_proxy = redirect_uri.replace(aws_nlb, domain)
    
    parameters = {'client_id': facebook_client_id,
                  'redirect_uri': redirect_uri_after_proxy,
                  'scope': 'public_profile,email'}
                  
    autorization_url = autorization_endpoint + '?' + urlencode(parameters)
    
    print('AUTH URL:', autorization_url)
    
    return autorization_url, redirect_uri, aws_nlb, domain, redirect_uri_after_proxy
    

def code_to_token(code):
            
    token_endpoint = 'https://graph.facebook.com/oauth/access_token'
    
    redirect_uri = url_for('login', _external=True, _scheme='https')
    
    # parameters = {'client_id': facebook_client_id,
    #               'client_secret': facebook_client_secret,
    #               'grant_type': 'authorization_code',
    #               'redirect_uri': redirect_uri,
    #               'code': code}
    
    # token_response = requests.get(token_endpoint, parameters)
    
    full_redirect_uri = f'{token_endpoint}?client_id={facebook_client_id}&client_secret={facebook_client_secret}&' + \
                        f'&grant_type=authorization_code&redirect_uri={redirect_uri}&code={code}'
                        
    token_response = requests.get(full_redirect_uri)
    
    token_response_json = token_response.json()
    access_token = token_response_json.get('access_token')
    
    return access_token, full_redirect_uri
    

def get_facebook_claims(access_token):
            
    me_endpoint = 'https://graph.facebook.com/me'
    
    parameters = {'fields': 'name,email,picture,short_name',
                  'access_token': access_token}
                  
    me_response = requests.get(me_endpoint, parameters)
    me_response_json = me_response.json()

    picture = me_response_json.get('picture')
    picture_data = picture.get('data') if picture else ""
    picture_url = picture_data.get('url') if picture_data else ""
    
    claims = {}
    
    claims['name'] = me_response_json.get('name')
    claims['email'] = me_response_json.get('email')
    claims['short_name'] = me_response_json.get('short_name')    
    claims['picture_url'] = picture_url
    
    return claims
    
    