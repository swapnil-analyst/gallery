import os
import random
import string
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

BASE_FOLDER = "static/images"

# Generate random event ID
def generate_event_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# HOME → Create Event
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form['password']
        event_id = generate_event_id()

        folder_path = os.path.join(BASE_FOLDER, event_id)
        os.makedirs(folder_path)

        # Store password in session (temporary)
        session[event_id] = password

        return redirect(f'/login/{event_id}')

    return render_template('create_event.html')


# LOGIN PAGE
@app.route('/login/<event_id>', methods=['GET', 'POST'])
def login(event_id):
    if request.method == 'POST':
        entered = request.form['password']

        if session.get(event_id) == entered:
            return redirect(f'/gallery/{event_id}')
        else:
            return "Wrong Password ❌"

    return render_template('login.html')


# GALLERY PAGE
@app.route('/gallery/<event_id>')
def gallery(event_id):
    folder = os.path.join(BASE_FOLDER, event_id)

    if not os.path.exists(folder):
        return "Invalid Event ❌"

    images = os.listdir(folder)
    return render_template('index.html', images=images, event_id=event_id)


# UPLOAD IMAGES
@app.route('/upload/<event_id>', methods=['POST'])
def upload(event_id):
    files = request.files.getlist('images')
    folder = os.path.join(BASE_FOLDER, event_id)

    for file in files:
        if file:
            file.save(os.path.join(folder, file.filename))

    return redirect(f'/gallery/{event_id}')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)