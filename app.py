import os
from flask import Flask
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
from bot import bot_post
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
scheduler = BackgroundScheduler()
jwt = JWTManager(app)

scheduler.configure({
    'apscheduler.jobstores.default': {
        'type': 'memory'  # Use an in-memory job store
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '1'  # Limit the number of workers
    },
    'apscheduler.timezone': 'UTC',  # Set the timezone (e.g., UTC)
})

# Schedule the task to run every 4 hours
scheduler.add_job(bot_post, 'interval', hours = 4, id='bot_post')

# Import routes after app and jwt initialization to avoid circular imports
from blueprints.routes import *

if __name__ == '__main__':
    scheduler.start()  # Start the scheduler when the application is run
    app.run(debug=True)
