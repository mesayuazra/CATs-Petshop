from flask import Flask, render_template, session,send_from_directory, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import re
import os
from werkzeug.utils import secure_filename 
from datetime import datetime

password = 'sparta'
cxn_str = f'mongodb://test:{password}@ac-6skehua-shard-00-00.eqimsea.mongodb.net:27017,ac-6skehua-shard-00-01.eqimsea.mongodb.net:27017,ac-6skehua-shard-00-02.eqimsea.mongodb.net:27017/?ssl=true&replicaSet=atlas-dad2x6-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0 '
client = MongoClient(cxn_str)
db = client.dbsparta_latihan

app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate)
app.secret_key = 'sparta'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



accessories = []  # Initialize accessories globally as an empty list

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', accessories=accessories, food=[])

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/food', methods=['GET'])
def food():
    food_list = list(db.food.find({}))
    return render_template('food.html', food=food_list)


@app.route('/accessories', methods=['GET'])
def accessories():
    accessories = list(db.accessories.find({}))
    return render_template('accessories.html', accessories=accessories)

@app.route('/grooming', methods=['GET'])
def grooming():
    return render_template('grooming.html')

@app.route('/ClinicHome', methods=['GET'])
def clinicHome():
    return render_template('clinicHome.html')

@app.route('/MedicalRecords', methods=['GET'])
def medicalRecords():
    return render_template('medicalRecords.html')

@app.route('/HealthCareServices', methods=['GET'])
def HCServices():
    return render_template('HCServices.html')

@app.route('/BookingHealthcareServices', methods=['GET'])
def bookHCServices():
    return render_template('BookHCServices.html')

@app.route('/check_login_status', methods=['GET'])
def check_login_status():
    logged_in = session.get('logged_in', False)
    if logged_in:
        username = session.get('username', 'User')
        return jsonify({'logged_in': True, 'username': username})
    return jsonify({'logged_in': False})

@app.route('/logout', methods=['GET'])
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
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'result': 'success', 'msg': 'success'})
        return jsonify({'result': 'failure', 'msg': 'Username or password incorrect'})
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
        
        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_regex, email):
            return jsonify({'result': 'failure', 'msg': 'Invalid email format'})
        if password != confirm_password:
            return jsonify({'result': 'failure', 'msg': 'Passwords do not match'})
        hashed_password = generate_password_hash(password)
        if db.users.find_one({'email': email}):
            return jsonify({'result': 'failure', 'msg': 'Email already registered'})
        
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

@app.route('/dashboard', methods=['GET'])
def dashboard():
    users = list(db.users.find({}, {'_id': 0, 'pet_id': 1, 'pet_name': 1, 'registration_date': 1}))
    return render_template('dashboard.html', users=users)

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'result': 'failure', 'msg': 'User not logged in'}), 401
    username = session['username']
    user = db.users.find_one({'email': username}, {'_id': 0, 'pet_id': 1, 'pet_name': 1, 'address': 1, 'phone': 1, 'email': 1, 'profile_photo': 1})
    if user:
        return jsonify(user), 200
    return jsonify({'result': 'failure', 'msg': 'User not found'}), 404

@app.route('/profile', methods=['GET'])
def profile():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    username = session['username']
    user = db.users.find_one({'email': username})
    if not user:
        return jsonify({'result': 'failure', 'msg': 'User not found'})
    profile_photo_url = user.get('profile_photo', None)
    return render_template('profile.html', user=user, profile_photo_url=profile_photo_url)

@app.route('/save_profile_photo', methods=['POST'])
def save_profile_photo():
    if 'profile_photo' not in request.files:
        return jsonify({'result': 'failure', 'msg': 'No file part'}), 400
    file = request.files['profile_photo']
    if file.filename == '':
        return jsonify({'result': 'failure', 'msg': 'No selected file'}), 
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        username = session['username']
        db.users.update_one({'email': username}, {'$set': {'profile_photo': filename}})
        return jsonify({'result': 'success', 'file_path': file_path}), 200
    return jsonify({'result': 'failure', 'msg': 'File type not allowed'}), 400

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/aturProduk', methods=['GET'])
def aturProduk():
    accessories_list = list(db.accessories.find({}))
    food_list = list(db.food.find({}))
    return render_template('manageProd.html', accessories=accessories_list, food=food_list)

@app.route('/api/add-accessory', methods=['POST'])
def add_accessory():
    if request.method == 'POST':
        try:
            name = request.form['productName']
            type = request.form['productType']
            category = request.form['productCategory']
            quantity = int(request.form['productQuantity'])
            price = float(request.form['productPrice'])

            # Handling file upload
            if 'productImage' in request.files:
                file = request.files['productImage']
                if file.filename == '':
                    filename = None
                elif file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    raise Exception('Invalid file type')
            else:
                filename = None

            # Add new accessory to the database
            new_accessory = {
                "name": name,
                "type": type,
                "category": category,
                "quantity": quantity,
                "price": price,
                "image": filename
            }
            # Assuming db is your MongoDB client and accessories is your collection
            db.accessories.insert_one(new_accessory)

            # Optionally, refresh accessories list from database
            # global accessories  # Remove global variable usage if not needed
            # accessories = list(db.accessories.find({}))

            return jsonify({"result": "success"})
        
        except Exception as e:
            return jsonify({"result": "error", "message": str(e)}), 400  # Return error message and HTTP status 400 (Bad Request) for client-side debugging

@app.route('/api/add-food', methods=['POST'])
def add_food():
    try:
        name = request.form['productName']
        type = request.form['productType']
        category = request.form['productCategory']
        quantity = int(request.form['productQuantity'])
        price = float(request.form['productPrice'])

        # Handling file upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None
        else:
            filename = None

        # Add new food to the database
        new_food = {
            "name": name,
            "type": type,
            "category": category,
            "quantity": quantity,
            "price": price,
            "image": filename
        }
        # Assuming db is your MongoDB client and foods is your collection
        db.food.insert_one(new_food)

        return jsonify({"result": "success"})
    
    except Exception as e:
        return jsonify({"result": "error", "message": str(e)}), 400


@app.route('/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'GET':
        accessory = db.accessories.find_one({'_id': ObjectId(product_id)})
        if not accessory:
            accessory = db.food.find_one({'_id': ObjectId(product_id)})
            if not accessory:
                return 'Product not found', 404
        return render_template('editProduct.html', product=accessory)
    elif request.method == 'POST':
        try:
            product_name = request.form['productName']
            product_type = request.form['productType']
            product_category = request.form['productCategory']
            product_quantity = int(request.form['productQuantity'])
            product_price = float(request.form['productPrice'])

            update_data = {
                'name': product_name,
                'type': product_type,
                'category': product_category,
                'quantity': product_quantity,
                'price': product_price
            }

            if 'productImage' in request.files:
                file = request.files['productImage']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    update_data['image'] = filename

            result = db.accessories.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
            if result.modified_count == 0:
                result = db.food.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})

            if result.modified_count == 1:
                return jsonify({'result': 'success', 'msg': 'Product updated successfully'})
            return jsonify({'result': 'failure', 'msg': 'Product not found or no changes made'})
        except Exception as e:
            return jsonify({'result': 'failure', 'msg': str(e)})
        
@app.route('/api/delete-product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        result = db.accessories.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count == 0:
            result = db.food.delete_one({'_id': ObjectId(product_id)})
            if result.deleted_count == 0:
                return jsonify({'result': 'failure', 'msg': 'Product not found'})
        return jsonify({'result': 'success', 'msg': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'result': 'failure', 'msg': str(e)})

@app.route('/tambahProduk', methods=['GET', 'POST'])
def tambahProduk():
    return render_template('addProd.html')


@app.route('/hapusProduk', methods=['GET', 'POST'])
def hapusProduk():
    return render_template('deleteProd.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
