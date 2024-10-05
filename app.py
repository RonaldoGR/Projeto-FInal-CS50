from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__,static_url_path='/static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
  return render_template("index.html")



@app.route('/login')
def login():
   return render_template("login.html")


@app.route('/register')
def register():
   return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

