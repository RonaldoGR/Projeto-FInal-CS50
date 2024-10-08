from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3


app = Flask(__name__,static_url_path='/static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def create_table():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 500.00,
    email TEXT NOT NULL,
    location TEXT
    )
    """)
    con.commit()
    con.close()

data = datetime.now()
year = data.year


def create_orders_table():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
    user_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER,
    value NUMERIC,
    total_order NUMERIC,
    time_order DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    con.commit()
    con.close()


   

# def teste():
#     print("Criando usuário de teste")
#     con = sqlite3.connect("database.db")
#     cur = con.cursor()
#     cur.execute("""
#         INSERT INTO users (id,name,age,hash,email, location)
#         VALUES(?,?,?,?,?,?)
#         """, (1, "Ronaldo",30,1234,"rgr@email.com", "Pelotas-RS"))
#     print("Criado pedidos de teste")

      

#     userId = cur.execute("SELECT id FROM users WHERE name = ?", ("Ronaldo",)).fetchone()[0]

#     cur.execute("""
#         INSERT INTO orders(user_id,item,quantity,value,total_order,time_order)
#         VALUES(?,?,?,?,?,?)
#         """, (userId,"Pizza de Calabresa", 2,30,60,data))

#     con.commit()
#     con.close()


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
  return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
   session.clear()

   if request.method == "POST":
      
      con = sqlite3.connect("database.db") 
      con.row_factory = sqlite3.Row #método que transforma as linhas em objetos
      cur = con.cursor()

      username = request.form.get("username")
      password = request.form.get("password")

      if not username:
         return "must be provide username"
      elif not password:
         return "must be provide password"
      
      user = cur.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchall()
      con.commit()

      if len(user) != 1 or not check_password_hash(user[0]["hash"],password):
         return "Invalid username and/or password 403"
      
      session["user_id"] = user[0]["id"]
      con.close()

      return redirect("/")
   
   return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
   session.clear()
   return redirect("/login")



@app.route('/register', methods=['GET','POST'])
def register():
   if request.method == "POST":
      
      con = sqlite3.connect("database.db")
      cur = con.cursor()

      name = request.form.get("name")
      if not name:
         return "400 must provide username"
      user = cur.execute("SELECT * FROM users WHERE name = ?",(name,)).fetchone()
      if user:
         return "400 username exists"
      
      email = request.form.get("email")
      if not email:
         return "400 must provide email"
      emailUser = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
      if emailUser:
         return "400 email exists"
      
      password = request.form.get("password")
      confirm = request.form.get("confirm")
      if not password or password != confirm:
         return "400 must provide password/ password is not confirmed"
    
      hash_password = generate_password_hash(
            password, method='scrypt', salt_length=16)
      
      location = request.form.get("location")
      if not location:
         return "400 must provide location"
      
      birthday = request.form.get("birthday")
      if not birthday:
         return "400 must provide birthday date"
      birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
      birthday_year = birthday_date.year
      age = year - birthday_year
      if (data.month, data.day) < (birthday_date.month, birthday_date.day):
         age -= 1

      try:
         cur.execute("""
                     INSERT INTO users(name, age, hash, email, location)
                     VALUES(?, ?, ?, ?, ?)
                     """, (name, age, hash_password, email, location))
         con.commit()
         new_user = cur.execute("SELECT id FROM users WHERE name = ?", (name,)).fetchone()
         session["user_id"] = new_user[0]
         
         con.close() 
         return redirect("/login")
      except Exception as e:
         print(f"ERROR: {e}")
         return "An error occurred, 500"
      
   return render_template("register.html")

if __name__ == "__main__":
    # Chama a função para criar a tabela antes de iniciar o servidor
    create_table()
    create_orders_table()
    # teste()
    app.run(debug=True, use_reloader=True, threaded = False)



