from core import app, models, users, aws_auth

from flask import render_template, redirect, url_for, flash, request, session

import botocore.exceptions
import boto3

cognito_client = boto3.client('cognito-idp')


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    # return redirect(aws_auth.get_sign_in_url())
    
    # next_url = request.args.get('next')
    
    if request.method == 'GET':
        
        return render_template("login.html", referrer=request.referrer)
        
    if request.method == 'POST':
        
        flash(f"Login form data: {request.form}", category='dark')
        
        login_response = users.login_user(request.form)
        
        if login_response['status'] == 'logged-in':
            
            session.permanent = True
            
            flash(f"Welcome, {session['username']}! Next: {request.args.get('next')}", category='dark')
            return redirect(request.args.get('next') or url_for('home'))
        
        else:
            
            flash(f"Login did not pass...", category='danger')
            return redirect(request.args.get('next') or url_for('home'))
            

@app.route('/register')
def register():
    
    sign_in_url = aws_auth.get_sign_in_url()
    
    register_url = sign_in_url.replace('login', 'signup', 1)
    
    return redirect(register_url)
    

@app.route("/logged-in")
def logged_in():
    
    access_token = aws_auth.get_access_token(request.args)
     
    response = cognito_client.get_user(AccessToken=access_token)
    
    username = response['Username']
    user_attributes = response['UserAttributes']
    user_sub = next(attribute['Value'] for attribute in user_attributes
                    if attribute['Name'] == 'sub')
    
    print('Access token:', access_token)
    print()
    print('Response:', response)
    print()
    print('User sub:', user_sub)
    print('User name:', username)
    
    
    print('ENV:', os.environ)
    
    session['username'] = username
    
    flash(f"Welcome, {username}!", category='dark')

    return redirect(request.args.get('next') or url_for('home'))
    

@app.route('/logout')
def logout():
    
    session['username'] = None
    
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
