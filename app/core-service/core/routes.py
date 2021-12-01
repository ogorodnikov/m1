import os
import requests

from flask import flash
from flask import url_for
from flask import session
from flask import request
from flask import redirect
from flask import send_file
from flask import render_template
from flask import send_from_directory

import boto3
import botocore.exceptions

from logging import getLogger


class Routes():
    
    def __init__(self, db, app, cognito, runner, facebook, telegram_bot):
        
        self.logger = getLogger(__name__)
        
        self.db = db
        self.app = app
        self.runner = runner
        self.cognito = cognito
        self.facebook = facebook
        self.telegram_bot = telegram_bot
        
        self.register_routes()
        
        self.logger.info(f"ROUTES initiated: {self}")       
        
        
    def register_routes(self):
        
        db = self.db
        app = self.app
        runner = self.runner
        cognito = self.cognito
        facebook = self.facebook
        telegram_bot = self.telegram_bot
        
        ###   Routes   ###

        @app.route("/")
        def root():
            
            if session.get('username'):
                redirect_url = url_for('get_algorithms')
            else:
                redirect_url = url_for('home')                
            
            return redirect(redirect_url)
            
        @app.route("/home")
        def home():
            return render_template("home.html")
            

        ###   Login   ###

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            
            session['login_referer'] = session.get('login_referer') or request.referrer
        
            flow = request.form.get('flow')
            code = request.args.get('code')
            
            login_url = url_for('login', _external=True, _scheme='https')
            
            if not (flow or code):
                
                return render_template("login.html")
            
            if flow == 'facebook':
                
                redirect_url = facebook.get_autorization_url(login_url)
        
            if code:
                
                self.facebook_login_user(code, login_url)
                redirect_url = session.pop('login_referer', None)
                
            if flow == 'register':
                
                self.register_user(request.form)
                self.sign_in_user(request.form)
                    
                redirect_url = session.pop('login_referer', None)
                
            if flow == 'sign-in':
                
                self.sign_in_user(request.form)
                
                redirect_url = session.pop('login_referer', None)
            
            return redirect(redirect_url)
                
        
        @app.route('/logout')
        def logout():
            
            session.pop('username', None)
            session.pop('email', None)
            session.pop('full_name', None)
            session.pop('picture_url', None)
            session.pop('facebook_token', None)
            
            flash(f"Logged out", category='info')
            
            return redirect(request.referrer)
            
        
        ###   Algorithms   ###
        
        @app.route('/algorithms')
        def get_algorithms():
            
            if request.args:
                try:
                    items = db.query_algorithms(request.args)
                except:
                    flash(f"Filter error)", category='warning')
                    items = db.get_all_algorithms()            
                
            else:
                items = db.get_all_algorithms()
        
            return render_template("algorithms.html", items=items)
            
            
        @app.route('/algorithms/<algorithm_id>')
        def get_algorithm(algorithm_id):
            
            algorithm = db.get_algorithm(algorithm_id)
            
            return render_template("algorithm.html", algorithm=algorithm)
            
            
        @app.route("/algorithms/<algorithm_id>/like", methods = ['GET'])
        def like_algorithm(algorithm_id):
            
            db.like_algorithm(algorithm_id)
        
            return redirect(request.referrer)
            
        
        @app.route("/algorithms/<algorithm_id>/run", methods = ['POST'])
        def run_algorithm(algorithm_id):
            
            run_values = request.form
            
            run_mode = run_values.get('run_mode')
            
            run_values_string = ', '.join(f'{key}: {value}' 
                                          for key, value in run_values.items()
                                          if key != 'run_mode')
            
            task_id = runner.run_algorithm(algorithm_id, run_values)
        
            task_url = f"/tasks?task_id={task_id}"
            
            run_message = (f"<a href='{task_url}' class='mb-0'"
                          f"target='_blank' rel='noopener noreferrer'>"
                          f"Task {task_id}</a>"
                          f"<hr class='mb-0 mt-1'>"
                          f"<p class='mb-0'>Algorithm: {algorithm_id}</p>"
                          f"<p class='mb-0'>Run mode: {run_mode}</p>"
                          f"<p class='mb-0'>Run values: {run_values_string}</p>")
                           
            flash(run_message, category='warning')
        
            return redirect(request.referrer)
            
        
        @app.route("/algorithms/<algorithm_id>/state")
        def set_algorithm_state(algorithm_id):
            
            is_enabled = request.args.get('enabled')
            is_enabled_bool = is_enabled.lower() != 'false'
            
            response = db.set_algorithm_state(algorithm_id, is_enabled_bool)
            
            flash(f"Algorithm {algorithm_id} - "
                  f"Set enabled: {is_enabled} - "
                  f"Response: {response}", category='warning')
            
            return redirect(f'/algorithms/{algorithm_id}')
        
        
        ###   Tasks   ###
        
        @app.route('/tasks')
        def get_tasks():
            
            tasks = db.get_all_tasks()
            task_id = request.args.get('task_id')
            
            if task_id:
                task = tasks[int(task_id)]
                
                # print(f"ROUTES task: {task}")
                # print(f"ROUTES task['task_result']: {task['task_result']}")
                
                return render_template("task.html", task=task)
                
            else:
                
                # print(f"ROUTES tasks: {tasks}")
                
                return render_template("tasks.html", tasks=tasks)
    
        
        @app.route('/download')
        def download():
            
            resource_id = request.args.get('resource_id')
            content_type = request.args.get('content_type')
            as_attachment = request.args.get('as_attachment', False)
            
            if content_type == 'statevector':
                
                filename = f"bloch_multivector_task_{resource_id}.png"
                s3_from_path = "figures/" + filename
                figure_stream = db.stream_figure_from_s3(s3_from_path)
                
                return send_file(
                    figure_stream, 
                    mimetype='image/png', 
                    download_name=filename,
                    as_attachment=as_attachment
                    )
                    
            elif content_type == 'diagram':
                return send_from_directory("static/diagrams", f"{resource_id}.png")
                
        
        ###   Admin   ###
        
        @app.route('/admin', methods=["GET", "POST"])
        def admin():
            
            command = request.form.get('command')
            
            if command == 'start_bot':
                telegram_bot.start()
                flash("Telegram bot started", category='info')
        
            elif command == 'stop_bot':
                telegram_bot.stop()
                flash("Telegram bot stopped", category='warning')
            
            elif command == 'add_test_data':
                db.add_test_data()
                flash(f"Test data added to m1-algorithms-table", category='warning')
                
            elif command == 'reset_application':
                flash(f"Exiting Flask application", category='danger')
                app.exit_application()
                
            elif command == 'start_runner':
                flash(f"Starting runner", category='success')
                runner.start()
        
            elif command == 'stop_runner':
                flash(f"Stopping runner", category='warning')
                runner.stop()
                
            elif command == 'purge_tasks':
                flash(f"Purging tasks", category='danger')        
                db.purge_tasks()
                db.purge_s3_folder('figures/')
                
            elif command == 'add_test_tasks':
                
                db.add_task('egcd', dict((('a', '345'), ('b', '455244237'), ('run_mode', 'classical'))))
                db.add_task('egcd', dict((('a', '345'), ('b', '455244237'), ('run_mode', 'classical'))))
                db.add_task('egcd', dict((('a', '345'), ('b', '455244237'), ('run_mode', 'classical'))))
                
                db.add_task('bernvaz', dict((('secret', '1010'), ('run_mode', 'simulator'))))
                db.add_task('bernvaz', dict((('secret', '1010'), ('run_mode', 'simulator'))))
                db.add_task('bernvaz', dict((('secret', '1010'), ('run_mode', 'simulator'))))

                flash(f"Added test tasks", category='primary')        
                
            elif command == 'test':
                flash(f"Test command", category='success')
                
                # db.update_task_attribute(1, 'task_log', [1, 2], if_exists=False)
                # db.update_task_attribute(5, 'logs', [7], append=True)
                # db.update_task_attribute(1, 'task_log', 'test_log')
                
                # db.add_status_update(7, 'Running', '')
                # db.get_status_updates()
                
                # db.update_task_attribute(1, 'result', 'test_result')
                
            return render_template("admin.html", environ=os.environ)
        
        
        @app.before_request
        def show_task_results():
            
            # print(f"ROUTES request.path {request.path}")
            
            if request.path == '/':
                return
            
            status_updates = db.get_status_updates()

            for status_update in status_updates:
                
                task_id, status, result = status_update
                
                if status == 'Running':
                    continue
                
                counts_dict = result.get('Counts')
                result_dict = result.get('Result')
                
                result_string = f"Result: None"
            
                if counts_dict:
                    
                    counts_string = ', '.join(f'{key}: {value}' 
                                              for key, value 
                                              in counts_dict.items())
                    
                    result_string = f"Counts: {counts_string}"
                    
                if result_dict:
                    
                    result_string = ', '.join(f'{key}: {value}' 
                                              for key, value 
                                              in result_dict.items())
                    
                    result_string = f"Result: {result_string}"
                
                task_url = f"/tasks?task_id={task_id}"
                
                status_message = (f"<a href='{task_url}' class='mb-0'"
                                  f"target='_blank' rel='noopener noreferrer'>"
                                  f"Task {task_id}</a>"
                                  f"<hr class='mb-0 mt-1'>"
                                  f"<p class='mb-0'>Status: {status}</p>"
                                  f"<p class='mb-0'>{result_string}</p>")
                
                flash(status_message, category='info')
    
    
    def facebook_login_user(self, code, login_url):
        
        try:
                    
            facebook_token = self.facebook.get_token_from_code(code, login_url)
            user_data = self.facebook.get_user_data(facebook_token)
            
            username = user_data.get('name')
            picture_url = user_data.get('picture_url')
            error = user_data.get('error')
            
            if error:
                raise UserWarning(error)
                
            self.cognito.populate_facebook_user(user_data)
            
            session['username'] = username
            session['picture_url'] = picture_url
            
            flash(f"Welcome, facebook user {username}!", category='warning')
                
        except Exception as exception:
            
            exception_message = f"Facebook login did not pass... {exception}"
            flash(exception_message, category='danger')
            
        
    def register_user(self, request_form):
    
        try:
        
            self.cognito.register_user(request_form)
            flash(f"New user registered", category='info')
    
        except Exception as exception:
            
            exception_message = f"Registration did not pass... {exception}"
            flash(exception_message, category='danger')
            
    
    def sign_in_user(self, request_form):
    
        try:
            
            logged_in_username = self.cognito.login_user(request_form)
            
            session.permanent = request_form.get('remember_me')
            session['username'] = logged_in_username
        
            flash(f"Welcome, {logged_in_username}!", category='warning')
            
        except Exception as exception:
            
            exception_message = f"Login did not pass... {exception}"
            flash(exception_message, category='danger')