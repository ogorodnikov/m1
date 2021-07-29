from core import app, models, users, fb, runner

from flask import render_template, redirect, url_for, flash, request, session

import boto3
import botocore.exceptions

import requests


###   Login   ###

@app.route('/login', methods = ['GET', 'POST'])
def login():
    
    session['login_referer'] = session.get('login_referer') or request.referrer

    flow = request.args.get('flow')
    code = request.args.get('code')
    
    if not (flow or code):
        
        return render_template("login.html")
    
    if flow == 'facebook':
        
        redirect_url = fb.get_autorization_url()

    if code:
        
        facebook_token = fb.code_to_token(code)
        redirect_url = fb.login_facebook_user(facebook_token)

    if flow == 'register':
        
        redirect_url = users.register_user(request.args)

    if flow == 'sign-in':
        
        redirect_url = users.login_user(request.args)

    return redirect(redirect_url)
        

@app.route('/logout')
def logout():
    
    session.pop('username', None)
    session.pop('picture_url', None)
    session.pop('facebook_token', None)
    
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
    
    run_values = request.form
    
    task_id = runner.run_algorithm(algorithm_id, run_values)
    
    flash(f"Task <a href='/tasks'>#{task_id}</a> scheduled: {algorithm_id}, {dict(run_values)}", category='warning')

    return redirect(request.referrer)
    

@app.route("/algorithms/<algorithm_id>/state", methods=['POST'])
def set_algorithm_state(algorithm_id):
    
    state = request.args.get('state')
    response = models.set_algorithm_state(algorithm_id, state)
    
    
    return response, 204
    

@app.route('/tasks')
def get_tasks():
    
    return render_template("tasks.html", tasks=runner.tasks, logs=runner.logs)


@app.before_request
def test():
    
    result_queue = runner.result_queue
    
    while not result_queue.empty():
        
        task_id, result = result_queue.get()
        flash(f"Task <a href='/tasks'>#{task_id}</a> done: {result}", category='info')

