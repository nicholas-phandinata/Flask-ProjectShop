from flask import render_template, session, request, redirect, url_for, flash
from shop import app, mysql, bcrypt, mail, Message, otp
from .form import RegistrationForm, LoginForm, VerifyForm
from random import *

@app.route('/admin')
def admin():
    if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Verified_Info FROM User_Info WHERE User_Name = %s", [session["username"]])
    verified_info = cur.fetchall()
    if verified_info[0][0] == "No":
        flash(f"Please Verify Your Account First!", 'danger')
        return redirect(url_for('validate'))
    cur.execute("SELECT Products.*, Brands.Name FROM Products JOIN Brands ON Products.Brand_Id = Brands.Brand_Id")
    products = cur.fetchall()
    return render_template('admin/index.html', title="Admin Page", products=products)

@app.route('/brands')
def brands():
    if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    sql_query = cur.execute("SELECT * FROM Brands")
    brands = cur.fetchall()
    return render_template('admin/brands.html', title="Brand Page", brands=brands)

@app.route('/categories')
def categories():
    if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    sql_query = cur.execute("SELECT * FROM Categories")
    categories = cur.fetchall()
    return render_template('admin/brands.html', title="Category Page", categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop("username", None)
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
          name = form.name.data
          username = form.username.data
          email = form.email.data
          hash_password = bcrypt.generate_password_hash(form.password.data)
          cur = mysql.connection.cursor()
          sql_query = cur.execute("SELECT User_Name FROM User_Info WHERE User_Name = %s", [username])
          if sql_query == 0:
              sql_query = "INSERT INTO User_Info (Name, User_Name, Email, Pwd) VALUES (%s, %s, %s, %s)"
              values = (name, username, email, hash_password)
              cur.execute(sql_query, values)
              mysql.connection.commit()
              cur.close()
              session["username"] = username
              flash(f"Account {username}, Successfully Registered!", "success")
              return redirect(request.args.get('next') or url_for('admin'))
          else:
              flash(f'Username {username}, Already Exist!', 'danger')
            #   return redirect(url_for('register'))
    return render_template('admin/register.html', form=form, title="Registration Page")

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if 'username' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Verified_Info FROM User_Info WHERE User_Name = %s", [session["username"]])
    v_info = cur.fetchall()
    if v_info[0][0] == "Verified":
        flash(f"Account Already Verified!", 'success')
        return redirect(url_for('admin'))
    form = VerifyForm(request.form)
    if request.method == 'POST' and form.validate():
        user_otp =  form.otp.data
        if otp == user_otp:
            update_query = "UPDATE User_Info set Verified_Info = %s WHERE User_Name = %s"
            values = ("Verified", session["username"])
            cur.execute(update_query,values)
            mysql.connection.commit()
            cur.close()
            flash('Account Successfully Verified!', 'success')
            return redirect(url_for('admin'))
        else:
            print(user_otp)
            flash('Incorrect OTP!', 'danger')
    return render_template('admin/verify.html', form=form, title="Verification Page")

@app.route('/sendOTP', methods=['GET', 'POST'])
def sendOTP():
    if 'username' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Email, Verified_Info FROM User_Info WHERE User_Name = %s", [session["username"]])
    info = cur.fetchall()
    if info[0][1] == "Verified":
        return redirect(url_for('admin'))
    global otp
    otp = randint(000000,999999)
    msg = Message(subject="OTP",sender='official.aboveaverage21@gmail.com',recipients=[info[0][0]])
    msg.body = str(otp)
    mail.send(msg)
    flash('Please Check Email For OTP!', 'success')
    return redirect(url_for('validate'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop("username", None)
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT Pwd FROM User_Info WHERE User_Name = %s", [username])
        if res > 0:
            data = cur.fetchone()
            hash_password = data[0]
            if bcrypt.check_password_hash(hash_password, password):
                session["username"] = username
                flash(f"Hello {username}, Welcome!", "success")
                cur.close()
                return redirect(request.args.get('next') or url_for('admin'))
            else:
                flash("Incorrect Password!", "danger")
                # return redirect(url_for('login'))
        else:
            flash("Incorrect Username or Username Not Found!", "danger")
            # return redirect(url_for('login'))
    return render_template('admin/login.html', form=form, title="Login Page")