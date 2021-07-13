import requests

from flask import flash, session, url_for

from core import app, users

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
    
    app.logger.info(f"AUTH redirect_uri: {redirect_uri}")
    app.logger.info(f"AUTH aws_nlb: {aws_nlb}")
    app.logger.info(f"AUTH domain: {domain}")
    app.logger.info(f"AUTH redirect_uri_after_proxy: {redirect_uri_after_proxy}")
    app.logger.info(f"AUTH autorization_url: {autorization_url}")
    
    return autorization_url
    

def code_to_token(code):
    
    token_endpoint = 'https://graph.facebook.com/oauth/access_token'
    
    redirect_uri = url_for('login', _external=True, _scheme='https')

    aws_nlb = app.config['AWS_NLB']
    domain = app.config['DOMAIN']
    redirect_uri_after_proxy = redirect_uri.replace(aws_nlb, domain)
    
    parameters = {'client_id': facebook_client_id,
                  'client_secret': facebook_client_secret,
                  'grant_type': 'authorization_code',
                  'redirect_uri': redirect_uri_after_proxy,
                  'code': code}
                  
    access_token_url = token_endpoint + '?' + urlencode(parameters)
    
    # token_response = requests.get(token_endpoint, parameters)
    token_response = requests.get(access_token_url)
    
    token_response_json = token_response.json()
    facebook_token = token_response_json.get('access_token')
    
    app.logger.info(f"AUTH code: {code}")
    app.logger.info(f"TOKEN redirect_uri: {redirect_uri}")
    app.logger.info(f"TOKEN aws_nlb: {aws_nlb}")
    app.logger.info(f"TOKEN domain: {domain}")
    app.logger.info(f"TOKEN redirect_uri_after_proxy: {redirect_uri_after_proxy}")
    app.logger.info(f"TOKEN parameters: {parameters}")
    app.logger.info(f"TOKEN access_token_url: {access_token_url}")
    app.logger.info(f"TOKEN token_response: {token_response}")
    app.logger.info(f"TOKEN token_response_json: {token_response_json}")   
    app.logger.info(f"TOKEN facebook_token: {facebook_token}")
    
    session['facebook_token'] = facebook_token    
    
    return facebook_token
    

def login_facebook_user(access_token):
            
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
    
    app.logger.info(f"CLAIMS me_endpoint: {me_endpoint}")
    app.logger.info(f"CLAIMS parameters: {parameters}")
    app.logger.info(f"CLAIMS me_response_json: {me_response_json}")
        
    login_referer = session['login_referer']
    session.pop('login_referer', None)
    
    users.populate_facebook_user()
        
    flash(f"Welcome, facebook user {session['username']}!", category='warning')
    
    return login_referer
    
    