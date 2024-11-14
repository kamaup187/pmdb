
# from gevent.pywsgi import WSGIServer
# from gevent import monkey

from app import create_app
# try:
#     from do_secrets import APP_SETTINGS
# except ImportError:
#     APP_SETTINGS = os.getenv('APP_SETTINGS')
# # from dapp import create_dapp

# configuration = os.getenv('APP_SETTINGS') or APP_SETTINGS

# monkey.patch_all()

app = create_app()

# def main():

#     # use gevent WSGI server instead of the Flask
#     # instead of 5000, you can define whatever port you want.
#     http = WSGIServer(('', 5000), app.wsgi_app) 

#     # Serve your application
#     http.serve_forever()


# if __name__ == '__main__':
#     main()

if __name__ == "__main__":
    app.run(port=5000,debug=True)

# if __name__ == "__main__":
#     app.run(port=5000,threaded=True)

# if __name__ == "__main__":
#     socketio.run(app, debug=True,port=5000)