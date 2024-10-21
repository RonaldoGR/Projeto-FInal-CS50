from flask import Flask, flash, redirect, render_template, request, session, url_for,json, jsonify
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3
import time


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
    birthday_date DATE,
    hash TEXT NOT NULL,
    email TEXT NOT NULL,
    full_adress TEXT
     )            
    """)
    con.commit()
    con.close()

   
def create_orders_table():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,              
    item TEXT,
    quantity INTEGER,
    value FLOAT,
    date_order TEXT,  
    time_order TEXT,
    date_delivery TEXT,            
    time_delivery TEXT,           
    FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    con.commit()
    con.close()    

data = datetime.now().strftime("Data: %d-%m-%Y")
horario =  datetime.now().strftime("%H:%M")
data_entrega = datetime.now().strftime("Data de entrega: %d-%m-%Y")
horario_entrega =  datetime.now().strftime("Horário de entrega: %H:%M")




   


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
   order_count = 0
   if isLoggedIn:
      con = sqlite3.connect("database.db")
      cur = con.cursor()
      order_count = cur.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
      con.commit()
      con.close()   
   return dict(isLoggedIn = isLoggedIn, order_count = order_count)


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
         full_adress = json.loads(json_data.get('full_adress'))
       
        
         username = json_data.get("name")
         email = json_data.get("email")
         password = json_data.get("password") 
         birthday = json_data.get("birthday")
        
         if not username or not email or not password or not birthday or not full_adress:
           return jsonify({"error": "Must provide all the fields"}), 400         
      
         user = cur.execute("SELECT * FROM users WHERE name = ?",(username,)).fetchone()         
         emailUser = cur.execute("SELECT * FROM users WHERE email = ?",(email,)).fetchone()       

         if user:
            return jsonify({"exists": "username"}), 400
         if emailUser:
            return jsonify({"exists": "email"}), 400
            
 
         hash_password = generate_password_hash(
               password, method='scrypt', salt_length=16)

            
         print("Inserting user into database")
         cur.execute("""
                        INSERT INTO users(name, birthday_date, hash, email, full_adress)
                        VALUES(?, ?, ?, ?, ?)
                        """, (username, birthday, hash_password, email, json.dumps(full_adress)))
         con.commit()
         new_user = cur.execute("SELECT id FROM users WHERE name = ?", (username,)).fetchone()
         session["user_id"] = new_user[0]
            
         con.close() 
         return jsonify({"redirect": "/login"}), 200
     
         
   return render_template("register.html")





@app.route("/menu", methods=["GET", "POST"])
def menu():
   isLoggedIn = "user_id" in session
   con = sqlite3.connect('database.db')
   cur = con.cursor()

  
   calabresa = request.form.get('calabresa')
   brownie = request.form.get('brownie')
   coca = request.form.get('coca')
   view_order = request.form.get('view_order')


   if not isLoggedIn:
      return render_template("menu.html")
   
   order = cur.execute("SELECT * FROM orders WHERE user_id = ?", (session["user_id"],)).fetchall()
   total =  cur.execute("""
                         SELECT SUM(value) as total FROM orders WHERE user_id = ?""", (session["user_id"],)).fetchone()
   
   


   if request.method == "POST" and isLoggedIn:            
     
       if calabresa:
         value = 50.00
         cur.execute("""
                           INSERT INTO orders(user_id,item,quantity,value)
                           VALUES(?, ?, ?, ?)
                           """, (session["user_id"], "Pizza de Calabresa", 1, value)) 
         con.commit()
       if brownie:
         value = 20.00
         cur.execute("""
                           INSERT INTO orders(user_id,item,quantity,value)
                           VALUES(?, ?, ?, ?)
                           """, (session["user_id"], "Brownie de Chocolate", 1, value)) 
         con.commit()
       if coca:
         print("Processing coca")
         value = 10.00
         cur.execute("""
                           INSERT INTO orders(user_id,item,quantity,value)
                           VALUES(?, ?, ?, ?)
                           """, (session["user_id"], "Coca-Cola", 1, value)) 
         con.commit()  
        
       order = cur.execute("SELECT * FROM orders WHERE user_id = ?", (session["user_id"],)).fetchall()
       total =  cur.execute("""
                         SELECT SUM(value) as total FROM orders WHERE user_id = ?""", (session["user_id"],)).fetchone()



       if view_order:
            return redirect("/client_order") 
       
   # if request.method == "GET" and request.is_json:
   #       html = render_template("menu.html", order=order, total=total[0])
   #       con.close()
   #       return jsonify({'html': html})


   con.close()      
   return render_template("menu.html",
                           isLoggedIn = isLoggedIn,
                           order = order,
                             total = total[0])




@app.route("/client_order", methods=["GET", "POST"])
@login_required
def client_order():
   
   con = sqlite3.connect("database.db")
   cur = con.cursor()
   order = cur.execute("SELECT * FROM orders WHERE user_id = ?", (session["user_id"],)).fetchall()
   total =  cur.execute("""
                         SELECT SUM(value) as total FROM orders WHERE user_id = ?""", (session["user_id"],)).fetchone()


   if request.method == 'POST':
      finalizacao = request.form.get('finalizar')
      confirmar_entrega = request.form.get('confirm')
      
      if finalizacao:
         adress = cur.execute("SELECT full_adress FROM users WHERE id = ?", (session["user_id"],)).fetchone()
       
         cur.execute("""
                                  UPDATE orders
                                 SET date_order = ?, time_order = ? 
                                 WHERE user_id = ? AND (time_order IS NULL OR time_order='') AND (date_order IS NULL OR date_order = 0)
                                  
                                   """, (data,horario,session["user_id"]))
         con.commit()

         horario_pedido = cur.execute("SELECT time_order FROM orders WHERE user_id =?", (session["user_id"],)).fetchone()

         return  render_template("client_order.html", order = order, total = total[0], partial = False, finalizacao = finalizacao, adress = json.loads(adress[0]), horario_pedido = horario_pedido[0])
      
      if confirmar_entrega:
           
             cur.execute("""
                                 UPDATE orders
                                 SET date_delivery = ?, time_delivery = ?
                                 WHERE user_id = ? AND time_delivery IS NULL AND date_delivery IS NULL
                                  
                                   """, (data_entrega,horario_entrega,session["user_id"]))
             con.commit()
             return render_template("index.html")  

      if request.is_json:
         json_data = request.get_json()
         remove = json_data.get('remove')
         cancelar = json_data.get('cancel')

         if remove:
            print("DELETANDO ITEM")
            
            cur.execute("DELETE FROM orders WHERE user_id = ? AND item_id = ?",(session["user_id"], remove))
            con.commit()

            cur.execute("DELETE FROM sqlite_sequence WHERE name = 'orders'")
            con.commit()

            order = cur.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY item_id", (session["user_id"],)).fetchall()

            for index, item in enumerate(order):
               cur.execute("UPDATE orders SET item_id = ? WHERE user_id = ? AND item_id=?", (index + 1, session["user_id"], item["item_id"]))
               con.commit()

            total =  cur.execute("""
                           SELECT SUM(value) as total FROM orders WHERE user_id = ?""", (session["user_id"],)).fetchone()
            
            if total is None:
               total = [0]
            
            order_count = cur.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (session["user_id"],)).fetchone()[0]

            if order_count == 0:
                con.close() 
                return jsonify({'redirect': True})
            
        
         
         if cancelar:
            print("CANCELANDO")
            cur.execute("DELETE FROM orders WHERE user_id = ?", (session["user_id"],)).fetchall()
            con.commit
            total =  cur.execute("""
                              SELECT SUM(value) as total FROM orders WHERE user_id = ?""", (session["user_id"],)).fetchone()
         con.close()
         html = render_template("index.html")
         return jsonify({'html': html})
         
         
     
   return render_template("client_order.html", order = order, total = total[0], partial = False)
   
   
 




if __name__ == "__main__":
    # Chama a função para criar a tabela antes de iniciar o servidor
    create_table()
    create_orders_table()
    # teste()
    app.run(debug=True, use_reloader=True, threaded = False)



