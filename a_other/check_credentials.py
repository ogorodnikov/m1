def check_credentials():
    
    import os
    
    os.environ['AWS_PROFILE'] = "default"
    os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
    
    print("MODELS available_profiles:", boto3.session.Session().available_profiles)
    
    boto3.setup_default_session(profile_name='default')
    
    table.scan()
    
    print("Connected to 'm1-algorithms-table'")