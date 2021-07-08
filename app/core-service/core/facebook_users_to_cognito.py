



def is_facebook_user_existing(email):
    pass
    
    

def register_facebook_user(login_form):
    
    username = login_form.get('name')
    email = login_form.get('email')
    picture_url = login_form.get('picture_url')
    
    sign_up_response = cognito_client.sign_up(ClientId=client_id,
                                              Username=username,
                                              Password=password)
    
    # confirmation_response = cognito_client.confirm_sign_up(ClientId=client_id,
    #                                                       Username=username,
    #                                                       ConfirmationCode='')
    
    confirmation_response = cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id,
                                                                 Username=username)

    print('Sign up response:', sign_up_response)
    print()
    
    print('Confirmation response:', confirmation_response)
    print()
    
    register_response = {'status': 'registered'}
    
    return register_response
    
    
def link_user(login_form):
    
    username = login_form.get('username')
    password = login_form.get('password')
    
    provider = cognito_client.describe_identity_provider(UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'],
                                                         ProviderName='Facebook')
                                                         
    providers = cognito_client.list_identity_providers(UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'])
    
    
    link_result = cognito_client.admin_link_provider_for_user(
        
        UserPoolId=app.config['AWS_COGNITO_USER_POOL_ID'],
    
            DestinationUser={
                'ProviderName': 'Cognito',
                # 'ProviderAttributeName': 'string',
                'ProviderAttributeValue': username
            },
            SourceUser={
                'ProviderName': 'Facebook',
                'ProviderAttributeName': 'Cognito_Subject',
                'ProviderAttributeValue': '4041300779272291'
            }
        )
    

    register_response = {'status': link_result}
    
    return register_response