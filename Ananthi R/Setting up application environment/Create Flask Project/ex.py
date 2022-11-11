from flask import Flask,redirect,url_for,request,json

app=Flask(__name__)

@app.route('/')
def home():
	return '<html><body><h1>hello world</h1></body></html>'

if __name__=="__main__":
    app.run(debug=True)
