from flask import Flask
from flask_jwt_extended import JWTManager

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "s8978786gudfr5ghgvghf"
jwt = JWTManager(app)

# Import routes after app and jwt initialization to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True)

