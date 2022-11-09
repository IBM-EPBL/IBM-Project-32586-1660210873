from flask import Flask,redirect,url_for,request,json

app=Flask(__name__)

users={"1":"siva", "2":"madhu", "3":"muthu", "4":"keerthi", "5":"vijay", "6":"mani"}

@app.route('/userdata',methods=['GET','POST'])
def api():
    if request.method=='GET':
        return users
    if request.method=='POST':
        userdata=request.json
        users.update(userdata)
        return 'userdata got inserted'
        
@app.route("/userdata/<id>",methods=['PUT'])
def update(id):
    userdata=request.form['item']
    users[str(id)]=userdata
    return 'userdata updated'
 
@app.route("/userdata/<id>",methods=['DELETE']) 
def delete(id):
    users.pop(str(id))
    return 'userdata deleted'

if __name__=='__main__':
    app.run(debug=True)
