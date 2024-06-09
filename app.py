from flask import Flask,redirect,url_for,render_template,request

app=Flask(__name__)
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

@app.route('/login',methods=['GET','POST'])
def login():
  return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
  return render_template('register.html')

@app.route('/inner',methods=['GET','POST'])
def inner():
  return render_template('inner-page.html')


if __name__ == '__main__':
  #DEBUG is SET to TRUE. CHANGE FOR PROD
  app.run('0.0.0.0',port=5000,debug=True)