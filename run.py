from app import create_app

app = create_app()

if __name__ == '__main__':
    # Host='0.0.0.0' allows access from other devices on the network
    app.run(host='0.0.0.0', debug=True, port=5000)
