from flask import Flask,render_template,request,redirect,url_for,session
from flask_session import Session
import ibm_db
import re
import smtplib

app = Flask(__name__)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
app.secret_key='a'

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vth49730;PWD=Y80y7E4L10eXRjNd",'','')

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    return render_template('profile.html')
   


@app.route('/profile')
def dash():
    return render_template('profile.html',username=session['username'])

@app.route('/addexpense',methods=['GET','POST'])
def expense():
    msg = ''
    if request.method == 'POST' :
        product = request.form['product']
        price = request.form['price']
        insert_sql2 = "INSERT INTO expense VALUES (?, ?, ?)"
        prep_stmt6 = ibm_db.prepare(conn, insert_sql2)
        ibm_db.bind_param(prep_stmt6, 1,session['username'])
        ibm_db.bind_param(prep_stmt6, 2, product)
        ibm_db.bind_param(prep_stmt6, 3, price)
        ibm_db.execute(prep_stmt6)

        # Code to update Limit Amount.............................................................

        sql = "SELECT AMOUNT FROM WALLETBALANCE  WHERE USERID=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1,session['username'])
        ibm_db.execute(prep_stmt)
        user= ibm_db.fetch_assoc(prep_stmt)
        dk=''
        
        if user:
            for i in user:
                dk=user[i]
                #break;

        # Code to get Limit Amount................................................................
        sqlh = "SELECT LIMITAMOUNT FROM SETLIMIT  WHERE USERID=?"
        prep_stmt1 = ibm_db.prepare(conn, sqlh)
        ibm_db.bind_param(prep_stmt1, 1,session['username'])
        ibm_db.execute(prep_stmt1)
        user1= ibm_db.fetch_assoc(prep_stmt1)
        siv=''
        
        if user1:
            for i in user1:
                siv=user1[i]

            result=int(dk)-int(price)
            sql1="UPDATE WALLETBALANCE SET AMOUNT=? WHERE USERID=?"
            prep_stmt1 = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(prep_stmt1, 1,result)
            ibm_db.bind_param(prep_stmt1, 2,session['username'])
            ibm_db.execute(prep_stmt1)

            if result<=siv:
                sendmail()

            
        msg = 'Product added!'
        return render_template('addexpense.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('addexpense.html', msg = msg)

    


@app.route('/viewexpense')
def viewexpense():
    msg = ''
    userid=[]
    product=[]
    price=[]
    stmt = ibm_db.exec_immediate(conn,"select * from expense")
    while ibm_db.fetch_row(stmt)!=False:
        userid.append(ibm_db.result(stmt, 0))
        product.append(ibm_db.result(stmt, 1))
        price.append(ibm_db.result(stmt, 2))
        print("USERID : ", ibm_db.result(stmt, 0), " Product Name : " ,ibm_db.result(stmt, 1), " Price : " ,ibm_db.result(stmt, 2))
    return render_template('viewexpense.html',msg = msg, userid = userid, product=product, price = price,lenuser=len(userid),user=session['username'])
    
   
  
@app.route('/viewExpense')
def pro():
    return render_template('profile.html')
    
@app.route('/index',methods=['GET','POST'])
def index():
    global userid
    msg= ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM webusers WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin'] = True
            session['id'] = account['USERNAME']
            userid=  account['USERNAME']
            session['username'] = account['USERNAME']
            
            msg = 'Logged in successfully !'
            return render_template('profile.html',username=session['username'])
        else:
            msg='Incorrect username/password !'
            return render_template('index.html',msg=msg)
    
@app.route('/register', methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        phoneno = request.form['phoneno']
        password = request.form['password']
        cpassword = request.form['cpassword']
        sql = "SELECT * FROM webusers WHERE username =?"
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
            insert_sql = "INSERT INTO  webusers VALUES (?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, phoneno)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.bind_param(prep_stmt, 5, cpassword)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template('index.html',msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
    

 
@app.route('/wallet', methods =['GET','POST'])
def addwallet():
    msg = ''
    if request.method=="POST":
        
        sql = "SELECT AMOUNT FROM WALLETBALANCE  WHERE USERID=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1,session['username'])
        ibm_db.execute(prep_stmt)
        user= ibm_db.fetch_assoc(prep_stmt)
        dk=''
        
        amount = request.form['sal']
        if user:
            for i in user:
                dk=user[i]
                #break;
            result=int(amount)+int(dk)
            sql1="UPDATE WALLETBALANCE SET AMOUNT=? WHERE USERID=?"
            prep_stmt1 = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(prep_stmt1, 1,result)
            ibm_db.bind_param(prep_stmt1, 2,session['username'])
            ibm_db.execute(prep_stmt1)
            session['result']=result
            return render_template('wallet.html', result=session['result'])
            
        else:
            
            insert_sql = "INSERT INTO walletbalance(userid,amount) VALUES (?,?)"
            prep_stmt2 = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt2, 1,session['username'])
            ibm_db.bind_param(prep_stmt2, 2,amount)
            ibm_db.execute(prep_stmt2)
            session['result']=amount
            msg = 'Amount updated successfully !'
            return render_template('wallet.html', result=session['result'])
    elif request.method == 'POST':
        msg = 'Please add again !'
    return render_template('wallet.html')
    

@app.route('/viewwallet')
def viewwallet():
    msg = ''
    userid=[]
    amount=[]
    stmt = ibm_db.exec_immediate(conn,"select * from walletbalance")
    while ibm_db.fetch_row(stmt)!=False:
        userid.append(ibm_db.result(stmt, 0))
        amount.append(ibm_db.result(stmt, 1))
        print("Userid : ", ibm_db.result(stmt, 0), " Amount : " ,ibm_db.result(stmt, 1))
    return render_template('viewwallet.html',msg = msg, userid = userid, amount = amount,lenuser=len(userid),user=session['username'])

    

@app.route('/limit', methods =['GET','POST'])
def addlimit():
    msg = ''
    if request.method=="POST":
        
        sql = "SELECT LIMITAMOUNT FROM SETLIMIT  WHERE USERID=?"
        prep_stmt3 = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt3, 1,session['username'])
        ibm_db.execute(prep_stmt3)
        user= ibm_db.fetch_assoc(prep_stmt3)
        dk=''
        
        limit = request.form['lim']
        if user:
            for i in user:
                dk=user[i]
                #break;
            limresult=int(limit)+int(dk)
            sql2="UPDATE SETLIMIT SET LIMITAMOUNT=? WHERE USERID=?"
            prep_stmt4 = ibm_db.prepare(conn, sql2)
            ibm_db.bind_param(prep_stmt4, 1,limresult)
            ibm_db.bind_param(prep_stmt4, 2,session['username'])
            ibm_db.execute(prep_stmt4)
            session['limit']=limit
            return render_template('wallet.html', limit=session['limit'])
            
        else:
            
            insert_sql = "INSERT INTO setlimit(userid,limitamount) VALUES (?,?)"
            prep_stmt5 = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt5, 1,session['username'])
            ibm_db.bind_param(prep_stmt5, 2,limit)
            ibm_db.execute(prep_stmt5)
            session['limit']=limit
            msg = 'Amount updated successfully !'
            return render_template('wallet.html', limit=session['limit'],msg=msg)
    elif request.method == 'POST':
        msg = 'Please add again !'
    return render_template('wallet.html')
    



@app.route('/viewlimit')
def viewlimit():
    msg = ''
    userid=[]
    limitamount=[]
    stmt = ibm_db.exec_immediate(conn,"select * from setlimit")
    while ibm_db.fetch_row(stmt)!=False:
        userid.append(ibm_db.result(stmt, 0))
        limitamount.append(ibm_db.result(stmt, 1))
        print("Userid : ", ibm_db.result(stmt, 0), " LimitAmount : " ,ibm_db.result(stmt, 1))
    return render_template('viewlimit.html',msg = msg, userid = userid, limitamount = limitamount,lenuser=len(userid),user=session['username'])

    

# CODE to send Mail...............................................

def sendmail():
    sq = "SELECT MAILID FROM WEBUSERS  WHERE USERNAME=?"
    prep_stmt2 = ibm_db.prepare(conn, sq)
    ibm_db.bind_param(prep_stmt2, 1,session['username'])
    ibm_db.execute(prep_stmt2)
    user2= ibm_db.fetch_assoc(prep_stmt2)
    mailid=''
        
    if user2:
        for i in user2:
            mailid=user2[i]
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("****************", "**************")
    s.sendmail('**************', mailid, 'You have exceeded the limit.So purchase accordingly!!')
    print('mail sent')




    
    
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('index.html')  
    
if __name__ == "__main__":
    app.run(debug=True)
