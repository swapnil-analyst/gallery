import os
import uuid
import random
import string
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Event

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/images'

db.init_app(app)

# Create DB
with app.app_context():
    db.create_all()


def generate_event_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

#Login
@app.route('/logout')
def logout():
    session.pop('event', None)
    return redirect('/')

# CREATE EVENT
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form['password']
        event_id = generate_event_id()

        hashed = generate_password_hash(password)
        
        name = request.form['event_name']  
        password = request.form.get('password')
        new_event = Event(id=event_id, name=name, password=hashed)
        db.session.add(new_event)
        db.session.commit()

        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], event_id), exist_ok=True)

        return redirect(f'/login/{event_id}')

    return render_template('create_event.html')


# LOGIN
@app.route('/login/<event_id>', methods=['GET', 'POST'])
def login(event_id):
    event = Event.query.get(event_id)

    if not event:
        return "Invalid Event ❌"

    if request.method == 'POST':
        password = request.form['password']

        if check_password_hash(event.password, password):
            session['event'] = event_id
            return redirect(f'/gallery/{event_id}')
        else:
            return "Wrong Password ❌"

    return render_template('login.html')


# GALLERY
# GALLERY 
@app.route('/gallery/<event_id>')
def gallery(event_id):
    if session.get('event') != event_id:
        return redirect(f'/login/{event_id}')

    folder = os.path.join(app.config['UPLOAD_FOLDER'], event_id)

    # create folder if missing
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 👇 ADD THIS
    event = Event.query.get(event_id)

    images = os.listdir(folder)
    count = len(images)

    return render_template(
        'index.html',   # or 'gallery.html' if you rename
        images=images,
        event_id=event_id,
        event=event,
        count=count
    )

@app.route('/upload/<event_id>', methods=['POST'])
def upload(event_id):
    if session.get('event') != event_id:
        return redirect(f'/login/{event_id}')

    files = request.files.getlist('images')
    folder = os.path.join(app.config['UPLOAD_FOLDER'], event_id)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    from werkzeug.utils import secure_filename

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            filepath = os.path.join(folder, filename)
            count = 1

            while os.path.exists(filepath):
                name, ext = filename.rsplit('.', 1)
                filename = f"{name}_{count}.{ext}"
                filepath = os.path.join(folder, filename)
                count += 1

            file.save(filepath)

    return redirect(f'/gallery/{event_id}')

# DELETE (REAL DELETE)
@app.route('/delete/<event_id>/<filename>')
def delete(event_id, filename):
    if session.get('event') != event_id:
        return redirect(f'/login/{event_id}')

    path = os.path.join(app.config['UPLOAD_FOLDER'], event_id, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect(f'/gallery/{event_id}')


if __name__ == '__main__':
    app.run(debug=True)