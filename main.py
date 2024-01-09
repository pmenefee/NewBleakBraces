from flask import Flask
from flask_session import Session
from flask_cors import CORS
from controllers.flask_routes import initialize_routes

app = Flask(__name__)
app.secret_key = '2030'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
Session(app)

initialize_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
