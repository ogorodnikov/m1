from core.app import create_app


app = create_app()

app.run_with_gunicorn()

# app.run_with_development_server()