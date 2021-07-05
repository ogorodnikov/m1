from core import app, models, egcd, aws_auth

from flask import render_template, redirect, url_for, flash, request, jsonify, session


import botocore.exceptions
import requests
import base64
import boto3
import os


cognito_client = boto3.client('cognito-idp')

###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    # return redirect(aws_auth.get_sign_in_url())
    
    next_url = request.args.get('next')
    
    if request.method == 'GET':
        return render_template("login.html", next=next_url)
        
    if request.method == 'POST':
        
        flash(f"Form data: {request.values}", category='dark')
        
        return redirect(next_url or url_for('home'))
    

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
    
    return redirect(request.args.get('next') or url_for('home'))




    

###   Algirithms   ###

@app.route("/")
@app.route("/home")
def home():
    
    # return jsonify({"message" : "M1 Core Service V.11"})
    
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
    
    # flash(f"Like counted: {response}!", category='warning')
    
    return redirect(url_for('get_algorithm', algorithm_id=algorithm_id))
    
    # return response, 204
    
    
@app.route("/algorithms/<algorithm_id>/run", methods = ['GET', 'POST'])
def run_algorithm(algorithm_id):
    
    # run_values = request.args.values()
    
    run_values = request.form
    
    flash(f"Run values: {run_values}!", category='warning')
    
    # run_int_values = map(int, run_values)
    
    # result = egcd.egcd(*run_int_values)
    
    # print(result)
    
    return redirect(url_for('get_algorithm', algorithm_id=algorithm_id))
    
    
    # for e in run_values.items():
    #     print(e)
    
    # if run_values is not None:
        
    #     service_response = runner.run_with_values(run_values)
        
    # else:

    #     service_response = runner.run_default()

    # flask_response = Response(service_response)
    # flask_response.headers["Content-Type"] = "application/json"

    return jsonify({"output": result})


@app.route("/algorithms/<algorithm_id>/state", methods=['POST'])
def set_algorithm_state(algorithm_id):
    
    state = request.args.get('state')
    response = models.set_algorithm_state(algorithm_id, state)
    
    return response, 204
