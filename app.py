from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3


# # Função para conectar ao banco de dados
# def get_db_connection():
#     conn = sqlite3.connect("database.db")
#     conn.row_factory = sqlite3.Row  # Permite que os resultados sejam tratados como dicionário
#     return conn

# # Função para criar a tabela, chamada na inicialização do app
# def create_table():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#     CREATE TABLE IF NOT EXISTS test_table (
#         id INTEGER PRIMARY KEY,
#         name TEXT
#     )
#     """)
#     conn.commit()
#     conn.close()





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
    # Chama a função para criar a tabela antes de iniciar o servidor
    create_table()
    create_orders_table()
    # teste()
    app.run(debug=True, use_reloader=True, threaded = False)



