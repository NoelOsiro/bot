import json
from flask import render_template, request, redirect, jsonify, url_for
from flask_jwt_extended import create_access_token
from blueprints.models import storage
from blueprints.models.user import User
from blueprints.models.tweet import Tweet, TweetImage
from blueprints.data.folders_data import folders, icons
from app import app


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Check if email already exists
        existing_email = storage.get(User, {'email': email})
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 400

        # Create a new user with a non-null password
        new_user = User(username=username, email=email,password=password)
        new_user.set_password(password)  # Set the password using your set_password method
        storage.new(new_user)
        storage.save()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = storage.get(User, {'email': email})
        if user and user.check_password(password):
            # Generate an access token
            access_token = create_access_token(identity=str(user.id))
            response = jsonify({'access_token': access_token})
            response.set_cookie('access_token', value=access_token)
            return redirect(url_for('dashboard'))
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    return render_template('login.html')

@app.route('/dashboard', methods=["GET"])
def dashboard():
    users = storage.all(User)
    tweets = storage.all(Tweet)
    return render_template('dashboard.html',folders=folders, icons=icons)

@app.route('/data', methods=["GET"])
def data():
    tweets = storage.all(Tweet)
    return render_template('data.html', tweets=tweets,folders=folders, icons=icons)

@app.route('/data/create', methods=["POST", "GET"])
def create_data():
    # Handle form submission to create new data items
    # Example: Create a new user
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        images = request.form.getlist('images')
        new_tweet = Tweet(title=title, text=text, images=images)
        storage.new(new_tweet)
        storage.save()
        return redirect(url_for('data'))
    
    return render_template('read_data.html',folders=folders, icons=icons)  # Redirect to read page after update

# # Update operation to modify existing data items
# @app.route('/data/<int:id>/update', methods=["POST"])
# def update_data(id):
#     # Handle form submission to update data items
#     # Example: Update an existing user
#     user = storage.get(User, id)
#     if user:
#         user.username = request.form['new_username']
#         user.email = request.form['new_email']
#         storage.save(user)
        
#     return render_template('read_data.html',folders=folders, icons=icons)  # Redirect to read page after update

# Delete operation to remove data items
@app.route('/data/<int:id>/delete', methods=["GET"])
def delete_data(id):
    # Handle request to delete data items
    # Example: Delete an existing user
    tweet = storage.get(Tweet, {'id':id})
    if tweet:
        storage.delete(tweet)
        storage.save()
    return redirect(url_for('data'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'data_file' not in request.files:
            return render_template('upload.html', error='No file part in the request',folders=folders, icons=icons)

        file = request.files['data_file']

        # Check if the file is a JSON file
        if file.filename == '' or not file.filename.endswith('.json'):
            return render_template('upload.html', error='Please upload a valid JSON file',folders=folders, icons=icons)

        # Read the JSON data from the uploaded file
        data = file.read()
        try:
            json_data = json.loads(data)
            for item in json_data:
                tweet = Tweet(title=item['title'], text=item['text'])
                storage.new(tweet)
                storage.save()

                if 'image_url' in item:
                    images = item['image_url']
                    for url in images:
                        image = TweetImage(url=url)
                        tweet.images.append(image)
                        storage.new(image)
                        storage.new(tweet)
                        storage.save()
            
            return render_template('upload.html', success='Database updated successfully',folders=folders, icons=icons)
        except Exception as e:
            storage.rollback()
            return render_template('upload.html', error=str(e),folders=folders, icons=icons)

    return render_template('upload.html',folders=folders, icons=icons)

