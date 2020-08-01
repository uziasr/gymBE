from app import app

# only purpose is to run the app
if __name__ == '__main__':
    # Schema()
    app.run(host='0.0.0.0')  # this should be set to True in development mode
