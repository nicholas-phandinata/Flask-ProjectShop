from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
from matplotlib.font_manager import json_dump
from shop import app, mysql, photos, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginFrom
import secrets
import os
import ast
import json
import pdfkit

@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    session.pop("customer", None)
    session.pop("customer_id", None)
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
          elif check_username != 0:
              flash(f'Username {username}, Already Exist!', 'danger')
          elif check_email != 0:
              flash(f'Email {email}, Already Exist!', 'danger')
    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    session.pop("customer", None)
    session.pop("customer_id", None)
    form = CustomerLoginFrom(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT Customer_ID, Pwd FROM Customers WHERE Email = %s", [email])
        if res > 0:
            data = cur.fetchone()
            hash_password = data[1]
            if bcrypt.check_password_hash(hash_password, password):
                session["customer"] = email
                session["customer_id"] = data[0]
                flash(f"Hello {email}, Welcome!", "success")
                return redirect(request.args.get('next') or url_for('home'))
            else:
                flash("Incorrect Password!", "danger")
                # return redirect(url_for('login'))
        else:
            flash("Incorrect Username or Username Not Found!", "danger")
            # return redirect(url_for('login'))         
    return render_template('customer/login.html', form=form)

@app.route('/customer/logout', methods=['GET','POST'])
def customerLogout():
    session.pop("customer", None)
    session.pop("customer_id", None)
    flash(f"Logged out successfully!", "success")
    return redirect(request.args.get('next') or url_for('home'))

@app.route('/getorder')
def get_order():
    if 'customer' in session:
        cur = mysql.connection.cursor()
        invoice = secrets.token_hex(5)
        try:
            sql_query = "INSERT INTO Customer_Orders (Invoice, Customer_ID, Orders) VALUES (%s, %s, %s)"
            orders = json.dumps(session['Shoppingcart'])
            values = (invoice, session["customer_id"], orders)
            cur.execute(sql_query, values)
            mysql.connection.commit()
            cur.close()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders'))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))
    else:
        return redirect(url_for('customerLogin'))

@app.route('/orders', methods=['GET','POST'])
def orders():
    if 'customer' in session:
        customer = session["customer"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT Customer_ID, Name, Username, Email, Address, Contact FROM Customers WHERE Email = %s", [session["customer"]])
        customer_info = cur.fetchone()
        cur.execute("SELECT * FROM Customer_Orders WHERE Customer_ID = %s AND Payment_Status = 'Pending'", [session["customer_id"]])
        get_orders = cur.fetchone()
        extract_orders = get_orders[5]
        orders = ast.literal_eval(extract_orders)
        subtotal = 0
        for key, product in orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subtotal += float(product['price']) * int(product['quantity'])
            subtotal -= discount
        grandtotal = "{:,.2f}".format(subtotal)

        if request.method =="POST":
            rendered =  render_template('customer/pdf.html', grandtotal=grandtotal, customer_info=customer_info, get_orders=get_orders, orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='atteched; filename=' + get_orders[1] + '.pdf'
            return response

        return render_template('customer/order.html', customer=customer, grandtotal=grandtotal, customer_info=customer_info, get_orders=get_orders, orders=orders)
    else:
        return redirect(url_for('customerLogin'))
