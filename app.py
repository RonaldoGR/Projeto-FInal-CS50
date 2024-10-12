from flask import Flask, flash, redirect, render_template, request, session, url_for,json, jsonify
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3
import json


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

date = datetime.now()
year = date.year


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


# Torna a variável isLoggedIn global para todas as rotas mesmo que não precise utilizá-la em algumas rotas
@app.context_processor
def inject_logged_in_status():
   isLoggedIn = "user_id" in session
  
   return dict(isLoggedIn = isLoggedIn)


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
  
   con = sqlite3.connect("database.db")
   cur = con.cursor()

   #Verificação se usuário e e-mail já estão cadastrados
   if request.method == "POST":
      if request.is_json:
         json_data = request.get_json()
         print(json_data)

         username = json_data.get("name")
         email = json_data.get("email")
         password = json_data.get("password") 
         birthday = json_data.get("birthday")
         location = json_data.get("location")

         print("Username:", username)
         print("Email:", email)
         print("Password:", password)
         print("Birthday:", birthday)
         print("Location:", location)
    

        
         if not username or not email or not password or not birthday or not location:
           return jsonify({"error": "Must provide all the fields"}), 400
         
      
         user = cur.execute("SELECT * FROM users WHERE name = ?",(username,)).fetchone()
         
         emailUser = cur.execute("SELECT * FROM users WHERE email = ?",(email,)).fetchone()
        

         if user:
            return jsonify({"exists": "username"}), 400
         if emailUser:
            return jsonify({"exists": "email"}), 400
   
         

         
      
         hash_password = generate_password_hash(
               password, method='scrypt', salt_length=16)
         
         
         if not birthday:
            birthday_date = None
            birthday_year = None
            age = 0
            return redirect("/register")
         try:            
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
            birthday_year = birthday_date.year
            age = year - birthday_year
            if (date.month, date.day) < (birthday_date.month, birthday_date.day):
                age -= 1
            print(username, age, hash_password, email, location)
            
            print("Inserting user into database")
            cur.execute("""
                        INSERT INTO users(name, age, hash, email, location)
                        VALUES(?, ?, ?, ?, ?)
                        """, (username, age, hash_password, email, location))
            con.commit()
            new_user = cur.execute("SELECT id FROM users WHERE name = ?", (username,)).fetchone()
            session["user_id"] = new_user[0]
            
            con.close() 
            return jsonify({"redirect": "/login"}), 200
         except Exception as e:
            print(f"ERROR: {e}")
            return jsonify({"error": "An error occurred" }), 500
         
   return render_template("register.html")






@app.route("/menu", methods=["GET", "POST"])
def menu():
   isLoggedIn = "user_id" in session
   print(f"O usuário está logado {isLoggedIn}")
   if request.method == "POST":
       return render_template("menu.html", isLoggedIn = isLoggedIn)
   return render_template("menu.html", isLoggedIn = isLoggedIn)






if __name__ == "__main__":
    # Chama a função para criar a tabela antes de iniciar o servidor
    create_table()
    create_orders_table()
    # teste()
    app.run(debug=True, use_reloader=True, threaded = False)



