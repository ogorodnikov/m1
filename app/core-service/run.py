from core.main import Main

main = Main()

# main.app.run_with_gunicorn()

main.app.run_with_development_server()