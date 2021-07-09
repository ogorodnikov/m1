from core import app, models, users, auth

from flask import render_template, redirect, url_for, flash, request, session

import boto3
import botocore.exceptions

import requests


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    session['login_referer'] = session.get('login_referer') or request.referrer

    
    flow = request.args.get('flow')
    
    if flow == 'facebook':
        
        autorization_url, redirect_uri, aws_nlb, domain, redirect_uri_after_proxy = auth.get_autorization_url()
        
        flash(f"AUTH redirect_uri: {redirect_uri}", category='info')
        flash(f"AUTH aws_nlb: {aws_nlb}", category='info')
        flash(f"AUTH domain: {domain}", category='info')
        flash(f"AUTH redirect_uri_after_proxy: {redirect_uri_after_proxy}", category='info')
        flash(f"AUTH autorization_url: {autorization_url}", category='info')
        
        return redirect(autorization_url)
        
        
    code = request.args.get('code')
    
    if code:
        
        flash(f"Code: {code}", category='info')
        
        facebook_token, redirect_uri = auth.code_to_token(code)
        
        claims = auth.get_facebook_claims(facebook_token)
        
        session['facebook_token'] = facebook_token
        session['username'] = claims['short_name']
        session['picture_url'] = claims['picture_url']
        
        login_referer = session['login_referer']
        session.pop('login_referer', None)
        
        flash(f"TOKEN Redirect URI: {redirect_uri}", category='info')
        flash(f"Token: {facebook_token}", category='info')
        flash(f"Claims: {claims}", category='info')
        
        flash(f"Welcome, facebook user {session['username']}!", category='warning')
        
        return redirect(login_referer)
        

    if flow == 'register':
        
        register_response = users.register_user(request.args)
        flash(f"New user registered", category='info')
        
        # return redirect(url_for('login', request.args))
        
        login_response = users.login_user(request.args)
        login_status = login_response['status']
        
        if login_status == 'logged-in':
            
            session.permanent = request.args.get('remember_me')
            
            flash(f"Remember me, {request.args.get('remember_me')}", category='info')
            flash(f"Welcome, {session['username']}!", category='warning')
            
        else:
            
            flash(f"Login did not pass... {login_status}", category='danger')
            
        
        login_referer = session['login_referer']
        session.pop('login_referer', None)
            
        return redirect(login_referer)
        
        
    if flow == 'sign-in':
    
        login_response = users.login_user(request.args)
        login_status = login_response['status']
        
        if login_status == 'logged-in':
            
            session.permanent = request.args.get('remember_me')
            
            flash(f"Remember me, {request.args.get('remember_me')}", category='info')
            flash(f"Welcome, {session['username']}!", category='warning')
            
        else:
            
            flash(f"Login did not pass... {login_status}", category='danger')
            
        
        login_referer = session['login_referer']
        session.pop('login_referer', None)
            
        return redirect(login_referer)
        
        
    return render_template("login.html")
                
                
                
        

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
