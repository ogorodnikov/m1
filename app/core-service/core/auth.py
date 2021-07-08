import requests

from flask import request

from urllib.parse import urlencode


def get_autorization_url():
    
    autorization_endpoint = 'https://www.facebook.com/v8.0/dialog/oauth'
    
    parameters = {'client_id': '355403372591689',
                  'redirect_uri': 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/login',
                  'scope': 'public_profile,email'}
                  
    # print(f">>>> Url for: {url_for('login')}, {request.referrer}")
                  
    autorization_url = autorization_endpoint + '?' + urlencode(parameters)
    
    return autorization_url
    

def code_to_token(code):
            
    token_endpoint = 'https://graph.facebook.com/oauth/access_token'
    
    parameters = {'client_id': '355403372591689',
                  'client_secret': '14a6e02a55e3c801993f58882e1b4ea1',
                  'grant_type': 'authorization_code',
                  'redirect_uri': 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/login',
                  'code': code}
    
    token_response = requests.get(token_endpoint, parameters)
    token_response_json = token_response.json()
    access_token = token_response_json.get('access_token')
    
    return access_token
    

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
    
    