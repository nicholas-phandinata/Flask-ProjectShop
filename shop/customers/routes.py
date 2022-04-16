from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
from shop import app, mysql, photos, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginFrom
import secrets
import os

@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    session.pop("username", None)
    form = CustomerRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
          name = form.name.data
          username = form.username.data
          email = form.email.data
          address = form.address.data
          contact = form.contact.data
          hash_password = bcrypt.generate_password_hash(form.password.data)
          cur = mysql.connection.cursor()
          check_username = cur.execute("SELECT Username FROM Customers WHERE Username = %s", [username])
          check_email = cur.execute("SELECT Email FROM Customers WHERE Email = %s", [email])
          if check_email == 0 and check_username == 0:
              sql_query = "INSERT INTO Customers (Name, Username, Email, Address, Contact, Pwd) VALUES (%s, %s, %s, %s, %s, %s)"
              values = (name, username, email, address, contact, hash_password)
              cur.execute(sql_query, values)
              mysql.connection.commit()
              cur.close()
              flash(f"Account {username}, Successfully Registered!", "success")
              return redirect(request.referrer)
          else:
              flash(f'Username {username}, Already Exist!', 'danger')
            #   return redirect(url_for('register'))
    return render_template('customer/register.html', form=form)