from core import app, models, users, fb, runner

from flask import render_template, redirect, url_for, flash, request, session
from flask import send_from_directory

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
    
    algorithm = models.get_algorithm(algorithm_id)
    
    return render_template("algorithm.html", algorithm=algorithm)
    
    
@app.route("/algorithms/<algorithm_id>/like", methods = ['GET'])
def like_algorithm(algorithm_id):
    
    response = models.like_algorithm(algorithm_id)

    return redirect(request.referrer)
    

@app.route("/algorithms/<algorithm_id>/run", methods = ['POST'])
def run_algorithm(algorithm_id):
    
    run_values = request.form
    
    task_id = runner.run_algorithm(algorithm_id, run_values)
    
    task_url = f"/tasks?task_id={task_id}"
    
    run_message = (f"<a href='{task_url}' class='mb-0'"
                   f"target='_blank' rel='noopener noreferrer'>"
                   f"Task {task_id}</a>"
                   f"<hr class='mb-0 mt-1'>"
                   f"<p class='mb-0'>Algorithm: {algorithm_id}</p>"
                   f"<p class='mb-0'>Test 21</p>"
                   f"<p class='mb-0'>Run values: {dict(run_values)}</p>")
    
    flash(run_message, category='warning')

    return redirect(request.referrer)
    

@app.route("/algorithms/<algorithm_id>/state")
def set_algorithm_state(algorithm_id):
    
    is_enabled = request.args.get('enabled')
    is_enabled_bool = is_enabled.lower() != 'false'
    
    response = models.set_algorithm_state(algorithm_id, is_enabled_bool)
    
    flash(f"Algorithm {algorithm_id} - "
          f"Set enabled: {is_enabled} - "
          f"Response: {response}", category='warning')
    
    return redirect(f'/algorithms/{algorithm_id}')
    

@app.route('/tasks')
def get_tasks():
    
    task_id_str = request.args.get('task_id')
    
    if task_id_str:
        
        task_id = int(task_id_str)
        
        task = runner.tasks[task_id]
        logs = runner.logs[task_id]
        
        return render_template("task.html", task_id=task_id, task=task, logs=logs)
        
    else:
    
        return render_template("tasks.html", tasks=runner.tasks, logs=runner.logs)
        

@app.route('/download')
def download():
    
    task_id = request.args.get('task_id')
    content = request.args.get('content')
    as_attachment = request.args.get('as_attachment', False)
    
    if content == 'statevector':
        
        path = "static/figures/"
        filename = f"bloch_multivector_task_{task_id}.png"
        
        return send_from_directory(path, filename, as_attachment=as_attachment)
        
    return redirect(request.referrer or url_for('home'))
    

@app.route('/admin', methods=["GET", "POST"])
def admin():
    
    command = request.form.get('command')
    
    if not command:
        
        return render_template("admin.html")
    
    telegram_bot = app.config.get('TELEGRAM_BOT')
    
    if command == 'start_bot':
        telegram_bot.start()
        flash("Telegram bot started", category='info')

    if command == 'stop_bot':
        telegram_bot.stop()
        flash("Telegram bot stopped", category='warning')
    
    if command == 'add_test_data':
        models.add_test_data()
        flash(f"Test data added to m1-algorithms-table", category='warning')
        
    if command == 'terminate':
        flash(f"Terminating", category='danger')
        runner.terminate_application("Terminated by admin")
    
    return render_template("admin.html")
    

@app.before_request
def show_task_results():
    
    for task_result in runner.get_task_results():
    
        task_id, result, status = task_result
        
        task_url = f"/tasks?task_id={task_id}"
        
        result_message = (f"<a href='{task_url}' class='mb-0'"
                          f"target='_blank' rel='noopener noreferrer'>"
                          f"Task {task_id}</a>"
                          f"<hr class='mb-0 mt-1'>"
                          f"<p class='mb-0'>Status: {status}</p>"
                          f"<p class='mb-0'>Result: {result}</p>")
        
        flash(result_message, category='info')

