from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re
from pymongo import MongoClient

password = 'sparta'
cxn_str = f'mongodb+srv://test:{password}@cluster0.eqimsea.mongodb.net/'
client = MongoClient(cxn_str)
db = client.dbsparta_latihan

app=Flask(__name__)

app.secret_key = 'sparta'  # Tetapkan secret key

@app.route('/',methods=['GET','POST'])
def home():
  return render_template('index.html')

@app.route('/about',methods=['GET','POST'])
def about():
  return render_template('about.html')

@app.route('/food',methods=['GET','POST'])
def food():
  return render_template('food.html')

@app.route('/accessories',methods=['GET','POST'])
def accessories():
  return render_template('accessories.html')

@app.route('/grooming',methods=['GET','POST'])
def grooming():
  return render_template('grooming.html')

@app.route('/ClinicHome',methods=['GET','POST'])
def clinicHome():
  return render_template('clinicHome.html')

@app.route('/MedicalRecords',methods=['GET','POST'])
def medicalRecords():
  return render_template('medicalRecords.html')

@app.route('/HealthCareServices',methods=['GET','POST'])
def HCServices():
  return render_template('HCServices.html')

@app.route('/BookingHealthcareServices',methods=['GET','POST'])
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
            return jsonify({'result': 'success','msg':'success'})
        else:
            # Jika autentikasi gagal, kembalikan pesan kesalahan
            return jsonify({'result': 'failure', 'msg': 'Invalid username or password'})
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
            return jsonify({'result': 'failure', 'msg': 'Invalid email format'})

        # Password validation
        if password != confirm_password:
            return jsonify({'result': 'failure', 'msg': 'Passwords do not match'})

        hashed_password = generate_password_hash(password)

        # Check if email already exists
        if db.users.find_one({'email': email}):
            return jsonify({'result': 'failure', 'msg': 'Email already registered'})

        # Insert new user into the database
        db.users.insert_one({
            'pet_id': pet_id,
            'pet_name': pet_name,
            'address': address,
            'phone': phone,
            'email': email,
            'password': hashed_password
        })

        return jsonify({'result': 'success'})

    return render_template('register.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
  return render_template('dashboard.html')

@app.route('/aturProduk',methods=['GET','POST'])
def aturProduk():
  return render_template('manageProd.html')

@app.route('/tambahProduk',methods=['GET','POST'])
def tambahProduk():
  return render_template('addProd.html')

@app.route('/apusProduk',methods=['GET','POST'])
def apusProduk():
  return render_template('deleteProd.html')

if __name__ == '__main__':
  #DEBUG is SET to TRUE. CHANGE FOR PROD
  app.run('0.0.0.0',port=5000,debug=True)