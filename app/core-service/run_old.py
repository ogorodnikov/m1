from core import app

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')
    
    