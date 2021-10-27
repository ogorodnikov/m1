# from core.app import create_app


# app = create_app()

# app.run_with_gunicorn()

# app.run_with_development_server()


from core.main import Main

main = Main()

main.app.run_with_gunicorn()