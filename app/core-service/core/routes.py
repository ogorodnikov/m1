from core import app, models, users, aws_auth

from flask import render_template, redirect, url_for, flash, request, session

import boto3
import botocore.exceptions

import urllib

cognito_client = boto3.client('cognito-idp')


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    next_url = request.args.get('next') or url_for('home')
    
    if request.method == 'GET':
        
        referer_parsed = urllib.parse.urlparse(request.referrer)
        referer_path = referer_parsed.path
        
        return render_template("login.html", referrer=referer_path)
        
    if request.method == 'POST':
        
        # flash(f"Login form data: {request.form}", category='dark')
        
        
        if request.form.get('action') == 'register':
            
            register_response = users.register_user(request.form)
            flash(f"New user registered", category='info')
            
        login_response = users.login_user(request.form)
        login_status = login_response['status']
        
        if login_status == 'logged-in':
            
            session.permanent = request.form.get('remember_me')
            
            parse_result = urllib.parse.urlparse(next_url)
            
            flash(f"Welcome, {session['username']}!", category='warning')
            flash(f"Next url:{next_url}!", category='info')
            flash(f"Parse result:{parse_result.path}!", category='info')            
            
            return redirect(next_url)
        
        else:
            
            flash(f"Login did not pass... {login_status}", category='danger')
            return redirect(next_url)
            

@app.route('/logout')
def logout():
    
    session.pop('username', None)
    
    flash(f"Logged out", category='info')
    
    return redirect(request.args.get('next') or url_for('home'))
    

###   Algirithms   ###

@app.route("/")
@app.route("/home")
def home():
    
    return render_template("home.html")
    

@app.route('/algorithms')
# @login_required
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
# @login_required
def like_algorithm(algorithm_id):
    
    response = models.like_algorithm(algorithm_id)

    return redirect(url_for('get_algorithm', algorithm_id=algorithm_id))
    

@app.route("/algorithms/<algorithm_id>/run", methods = ['GET', 'POST'])
def run_algorithm(algorithm_id):
    
    run_values = tuple(request.form.values())
    run_result = models.run_algorithm(algorithm_id, run_values)
    
    flash(f"Running with values: {run_values}", category='warning')
    flash(f"Result: {run_result}", category='info')
    
    return redirect(url_for('get_algorithm', algorithm_id=algorithm_id))
    

@app.route("/algorithms/<algorithm_id>/state", methods=['POST'])
def set_algorithm_state(algorithm_id):
    
    state = request.args.get('state')
    response = models.set_algorithm_state(algorithm_id, state)
    
    return response, 204
