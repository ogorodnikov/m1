from core import app, gunicorn_app

# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')
    
gunicorn_app.run()
    