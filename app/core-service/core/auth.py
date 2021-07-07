import requests


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