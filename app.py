from flask import Flask, render_template,send_from_directory, session, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re
from pymongo import MongoClient
from datetime import datetime  
import os
from werkzeug.utils import secure_filename
from bson import ObjectId

password = 'sparta'
cxn_str = f'mongodb://test:{password}@ac-6skehua-shard-00-00.eqimsea.mongodb.net:27017,ac-6skehua-shard-00-01.eqimsea.mongodb.net:27017,ac-6skehua-shard-00-02.eqimsea.mongodb.net:27017/?ssl=true&replicaSet=atlas-dad2x6-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0 '
client = MongoClient(cxn_str)
db = client.dbsparta_latihan

app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate)
app.secret_key = 'sparta'  # Tetapkan secret key

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/food', methods=['GET', 'POST'])
def food():
    return render_template('food.html')

@app.route('/accessories', methods=['GET', 'POST'])
def accessories():
    return render_template('accessories.html')

@app.route('/grooming', methods=['GET', 'POST'])
def grooming():
    return render_template('grooming.html')

@app.route('/ClinicHome', methods=['GET', 'POST'])
def clinicHome():
    return render_template('clinicHome.html')

@app.route('/MedicalRecords', methods=['GET', 'POST'])
def medicalRecords():
    return render_template('medicalRecords.html')

@app.route('/HealthCareServices', methods=['GET', 'POST'])
def HCServices():
    return render_template('HCServices.html')

@app.route('/BookingHealthcareServices', methods=['GET', 'POST'])
def bookHCServices():
    return render_template('BookHCServices.html')

@app.route('/check_login_status')
def check_login_status():
    logged_in = session.get('logged_in', False)
    if logged_in:
        username = session.get('username', 'User')
        return jsonify({'logged_in': True, 'username': username})
    else:
        return jsonify({'logged_in': False})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username_give']
        password = request.form['password_give']

        user = db.users.find_one({'email': username})

        if user and check_password_hash(user['password'], password):
            # Jika autentikasi berhasil, set status login ke sesi
            session['logged_in'] = True
            session['username'] = username
            # Redirect ke halaman utama atau halaman yang diinginkan setelah login
            return jsonify({'result': 'success', 'msg': 'success'})
        else:
            # Jika autentikasi gagal, kembalikan pesan kesalahan
            return jsonify({'result': 'failure', 'msg': 'Username atau password salah'})
    # Jika metode adalah GET, tampilkan halaman login
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pet_id = request.form['pet_id']
        pet_name = request.form['pet_name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Email validation
        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_regex, email):
            return jsonify({'result': 'failure', 'msg': 'Format email tidak valid'})

        # Password validation
        if password != confirm_password:
            return jsonify({'result': 'failure', 'msg': 'Password Anda salah'})

        hashed_password = generate_password_hash(password)

        # Check if email already exists
        if db.users.find_one({'email': email}):
            return jsonify({'result': 'failure', 'msg': 'Email sudah terdaftar'})

        # Insert new user into the database with the registration date
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.users.insert_one({
            'pet_id': pet_id,
            'pet_name': pet_name,
            'address': address,
            'phone': phone,
            'email': email,
            'password': hashed_password,
            'registration_date': registration_date
        })

        return jsonify({'result': 'success'})

    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Fetch user data from MongoDB
    users = list(db.users.find({}, {'_id': 0, 'pet_id': 1, 'pet_name': 1, 'registration_date': 1}))
    return render_template('dashboard.html', users=users)

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'result': 'failure', 'msg': 'User not logged in'}), 401

    username = session['username']
    user = db.users.find_one({'email': username}, {'_id': 0, 'pet_id': 1, 'pet_name': 1, 'address': 1, 'phone': 1, 'email': 1, 'profile_photo': 1})

    if user:
        # Replace the profile_photo path with a URL if using a web server or serving static files
        # Example: user['profile_photo'] = url_for('static', filename=user['profile_photo'])
        return jsonify(user), 200
    else:
        return jsonify({'result': 'failure', 'msg': 'User not found'}), 404

@app.route('/profile', methods=['GET'])
def profile():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))  # Redirect ke halaman login jika pengguna tidak terautentikasi

    # Ambil data pengguna dari MongoDB
    username = session['username']
    user = db.users.find_one({'email': username})

    if not user:
        return jsonify({'result': 'failure', 'msg': 'User not found'})

    # Ambil URL gambar profil dari MongoDB, jika ada
    profile_photo_url = user.get('profile_photo', None)

    return render_template('profile.html', user=user, profile_photo_url=profile_photo_url)

@app.route('/save_profile_photo', methods=['POST'])
def save_profile_photo():
    if 'profile_photo' not in request.files:
        return jsonify({'result': 'failure', 'msg': 'No file part'}), 400

    file = request.files['profile_photo']
    if file.filename == '':
        return jsonify({'result': 'failure', 'msg': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        username = session['username']
        db.users.update_one(
            {'email': username},
            {'$set': {'profile_photo': filename}}
        )

        return jsonify({'result': 'success', 'file_path': file_path}), 200

    return jsonify({'result': 'failure', 'msg': 'File type not allowed'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/aturProduk', methods=['GET', 'POST'])
def aturProduk():
    accessories = list(db.accessories.find({}))
    food = list(db.food.find({}))
    return render_template('manageProd.html', accessories=accessories, food=food)
@app.route('/api/add-accessory', methods=['POST'])
def add_accessory():
    product_name = request.form['productName']
    product_type = request.form['productType']
    product_category = request.form['productCategory']
    product_quantity = int(request.form['productQuantity'])
    product_price = float(request.form['productPrice'])
    
    if 'productImage' in request.files:
        product_image = request.files['productImage']
        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({'result': 'failure', 'msg': 'Invalid image format'})
    else:
        image_url = None

    db.accessories.insert_one({
        'name': product_name,
        'type': product_type,
        'category': product_category,
        'quantity': product_quantity,
        'price': product_price,
        'image_url': image_url
    })

    return jsonify({'result': 'success', 'msg': 'Accessory added successfully'})
@app.route('/api/add-food', methods=['POST'])
def add_food():
    product_name = request.form['productName']
    product_type = request.form['productType']
    product_category = request.form['productCategory']
    product_quantity = int(request.form['productQuantity'])
    product_price = float(request.form['productPrice'])

    if 'productImage' in request.files:
        product_image = request.files['productImage']
        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({'result': 'failure', 'msg': 'Invalid image format'})
    else:
        image_url = None

    db.food.insert_one({
        'name': product_name,
        'type': product_type,
        'category': product_category,
        'quantity': product_quantity,
        'price': product_price,
        'image_url': image_url
    })

    return jsonify({'result': 'success', 'msg': 'Food added successfully'})


@app.route('/tambahProduk', methods=['GET', 'POST'])
def tambahProduk():
    return render_template('addProd.html')

@app.route('/hapusProduk', methods=['GET', 'POST'])
def apusProduk():
    return render_template('deleteProd.html')

if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0', port=5000, debug=True)
