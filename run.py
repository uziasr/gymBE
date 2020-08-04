from app import create_app

# only purpose is to run the app
app = create_app()

if __name__ == '__main__':
    # Schema()
    app.run(host='0.0.0.0')  # this should be set to True in development mode
