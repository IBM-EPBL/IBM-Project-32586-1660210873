from flask import Flask,render_template,request,redirect,url_for,session
import ibm_db
import re
app = Flask(__name__)

app.secret_key='a'


conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vth49730;PWD=Y80y7E4L10eXRjNd",'','')

@app.route('/')
def home():
    return render_template('register.html')
    
    
@app.route('/register', methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        phoneno = request.form['phoneno']
        password = request.form['password']
        cpassword = request.form['cpassword']
        sql = "SELECT * FROM registeredusers WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO  registeredusers VALUES (?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, phoneno)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.bind_param(prep_stmt, 5, cpassword)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template('welcome.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
  
    
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('register.html')  
    
if __name__ == "__main__":
    app.run(debug=True)