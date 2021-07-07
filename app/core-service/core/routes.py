from core import app, models, users, auth

from flask import render_template, redirect, url_for, flash, request, session

import boto3
import botocore.exceptions

import requests
from urllib.parse import urlencode


cognito_client = boto3.client('cognito-idp')


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    session['login_referer'] = session.get('login_referer') or request.referrer


    if request.method == 'GET':
        
        
        facebook = request.args.get('facebook')
        
        if facebook:
        
            autorization_endpoint = 'https://www.facebook.com/v8.0/dialog/oauth'
            
            parameters = {'client_id': '355403372591689',
                          'redirect_uri': 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/login',
                          'scope': 'public_profile,email'}
                          
            autorization_url = autorization_endpoint + '?' + urlencode(parameters)

            return redirect(autorization_url)
            
        
        code = request.args.get('code')
        
        if code:
            
            access_token = auth.code_to_token(code)
            session['token'] = access_token
            
            
            me_endpoint = 'https://graph.facebook.com/me'
            
            parameters = {'fields': 'name,email,picture,short_name',
                          'access_token': access_token}
                          
            me_response = requests.get(me_endpoint, parameters)
            me_response_json = me_response.json()
            
            name = me_response_json.get('name')
            email = me_response_json.get('email')
            picture = me_response_json.get('picture')
            short_name = me_response_json.get('short_name')
            
            picture_url = picture.get('data').get('url') if picture else ""
            
            session['username'] = short_name
            session['picture_url'] = picture_url
            
            flash(f"Welcome, facebook user {session['username']}!", category='warning')
            
            login_referer = session['login_referer']
            session.pop('login_referer', None)
            
            return redirect(login_referer)
            

        return render_template("login.html")
        
        
    if request.method == 'POST':
        
        if request.form.get('action') == 'register':
            
            register_response = users.register_user(request.form)
            flash(f"New user registered", category='info')
            
            
        login_response = users.login_user(request.form)
        login_status = login_response['status']
        
        if login_status == 'logged-in':
            
            session.permanent = request.form.get('remember_me')
            
            flash(f"Welcome, {session['username']}!", category='warning')
            
        else:
            
            flash(f"Login did not pass... {login_status}", category='danger')
            
        
        login_referer = session['login_referer']
        session.pop('login_referer', None)
            
        return redirect(login_referer)
        

@app.route('/logout')
def logout():
    
    session.pop('username', None)
    session.pop('picture_url', None)
    
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
