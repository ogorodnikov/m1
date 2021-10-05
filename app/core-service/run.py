from core.app import app


app.run_with_gunicorn()


# developement_server_parameters = {
#     'host': "0.0.0.0", 
#     'port': 8080, 
#     'debug': True, 
#     'use_reloader': False, 
#     'reloader_type': 'stat'
# }

# app.run_with_developement_server(**developement_server_parameters)
