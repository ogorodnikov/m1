
def login():
    domain_name = 'm1.ogoro.me'
    region = 'us-east-1'
    client_id = '196332284574'
    redirect_uri = 'logged-in'

    loginendpoint = 'https://' + domain_name + '.auth.' + region + '.amazoncognito.com/oauth2/authorize?'
    response_type = 'code'
    scope = 'openid profile'
    
    loginurl = loginendpoint + 'response_type=' + response_type + '&client_id=' + client_id + '&scope=' + scope + '&redirect_uri=' + redirect_uri


    print(loginurl)
    
    # return redirect(loginurl)
    
if __name__ == "__main__":
    
    login()