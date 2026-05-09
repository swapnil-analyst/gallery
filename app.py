import os
import random
import string
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from models import db, Event, Image
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="dxprjwwji",
    api_key="749491621426565",
    api_secret="xLfQG9wz1ncs6cADIu0t9E1yJvk"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
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

    images = Image.query.filter_by(event_id=event_id).all()
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

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    images_to_save = []

    for file in files:
        if file and allowed_file(file.filename):
            result = cloudinary.uploader.upload(
                file,
                upload_preset="gallery_upload"
               )
            images_to_save.append(
                Image(event_id=event_id, url=result['secure_url'])
            )

    for img in images_to_save:
        db.session.add(img)

    db.session.commit()

    return redirect(f'/gallery/{event_id}')

# DELETE (REAL DELETE)
@app.route('/delete/<int:image_id>')
def delete(image_id):
    image = Image.query.get(image_id)

    if image:
        db.session.delete(image)
        db.session.commit()

    return redirect(request.referrer)

if __name__ == '__main__':
        app.run(debug=True)