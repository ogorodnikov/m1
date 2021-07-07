from core import app, models, users, aws_auth

from flask import render_template, redirect, url_for, flash, request, session

import boto3
import botocore.exceptions

import requests


cognito_client = boto3.client('cognito-idp')


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    next_url = request.args.get('next') or url_for('home')
    
    if request.method == 'GET':
        
        code = request.args.get('code')
        
        if code:
            
            flash(f"Code: {code}", category='info')
            
            token_endpoint = 'https://graph.facebook.com/oauth/access_token'
            
            parameters = {'client_id': '355403372591689',
                          'client_secret': '14a6e02a55e3c801993f58882e1b4ea1',
                          'grant_type': 'authorization_code',
                          'redirect_uri': 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/login',
                          'code': code}
            
            token_response = requests.get(token_endpoint, parameters)
            token_response_json = token_response.json()
            access_token = token_response_json.get('access_token')
            
            app.config['token'] = access_token
            
            flash(f"Token response: {token_response_json}", category='warning')
            flash(f"Token: {access_token}", category='danger')
            
            
            
            me_endpoint = 'https://graph.facebook.com/me'
            
            parameters = {'fields': 'name,email,picture',
                          'access_token': access_token}
                          
            me_response = requests.get(me_endpoint, parameters)
            me_response_json = me_response.json()
            
            name = me_response_json.get('name')
            email = me_response_json.get('email')
            picture = me_response_json.get('picture')
            
            picture_url = picture.get('data').get('url') if picture else ""
            
            flash(f"Name: {name}", category='info')
            flash(f"Email: {email}", category='info')
            flash(f"Picture URL: {picture_url} <a href=”{picture_url}”><\a>", category='info')
            
            
        
        return render_template("login.html", referrer=request.referrer, code=code)
        
    if request.method == 'POST':
        
        if request.form.get('action') == 'register':
            
            register_response = users.register_user(request.form)
            flash(f"New user registered", category='info')
            
            
            
        if request.form.get('action') == 'facebook':
            
            facebook_response = users.facebook(request.form)
            flash(f"Facebook: {facebook_response}", category='info')          


            
        login_response = users.login_user(request.form)
        login_status = login_response['status']
        
        if login_status == 'logged-in':
            
            session.permanent = request.form.get('remember_me')
            
            flash(f"Welcome, {session['username']}!", category='warning')
            
        else:
            
            flash(f"Login did not pass... {login_status}", category='danger')
        
        return redirect(next_url)
            

@app.route('/logout')
def logout():
    
    session.pop('username', None)
    
    flash(f"Logged out", category='info')
    
    return redirect(request.referrer)
    

###   Algirithms   ###

@app.route("/")
@app.route("/home")
def home():
    
    return render_template("home.html")
    

@app.route('/algorithms')
def get_algorithms():
    
    if not request.args:
        
        items = models.get_all_algorithms()
    
    else:
        
        try:
            items = models.query_algorithms(request.args)
            
        except botocore.exceptions.ClientError:
            items = models.get_all_algorithms()
        
    return render_template("algorithms.html", items=items)
    
    
@app.route('/algorithms/<algorithm_id>')
def get_algorithm(algorithm_id):
    
    item = models.get_algorithm(algorithm_id)
    
    return render_template("algorithm.html", item=item)
    
    
@app.route("/algorithms/<algorithm_id>/like", methods = ['GET'])
def like_algorithm(algorithm_id):
    
    response = models.like_algorithm(algorithm_id)

    return redirect(request.referrer)
    

@app.route("/algorithms/<algorithm_id>/run", methods = ['POST'])
def run_algorithm(algorithm_id):
    
    run_values = tuple(request.form.values())
    run_result = models.run_algorithm(algorithm_id, run_values)
    
    flash(f"Running with values: {run_values}", category='warning')
    flash(f"Result: {run_result}", category='info')
    
    return redirect(request.referrer)
    

@app.route("/algorithms/<algorithm_id>/state", methods=['POST'])
def set_algorithm_state(algorithm_id):
    
    state = request.args.get('state')
    response = models.set_algorithm_state(algorithm_id, state)
    
    return response, 204
