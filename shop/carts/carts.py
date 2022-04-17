from crypt import methods
from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import app, mysql
from shop.products.routes import displayBrands, displayCategories

def MergeDicts(dict1,dict2):
    if isinstance(dict1, list) and isinstance(dict2,list):
        return dict1  + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        color = request.form.get('colors')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Products WHERE Product_Id = %s", [product_id])
        product = list(cur.fetchone())
        rupiah = float(product[2])
        product[2] = rupiah

        if product_id and quantity and color and request.method == "POST":
              DictItems = {product_id:{'name':product[1],'price':product[2],
              'discount':product[3],'color':color,'quantity':quantity,'image':product[10], 
              'colors':product[5], 'quantities':product[4]}}

              if 'Shoppingcart' in session:
                    if product_id in session['Shoppingcart']:
                        for key, item in session['Shoppingcart'].items():
                            if int(key) == int(product_id):
                                session.modified = True
                                item['quantity'] = item['quantity'] + quantity
                    else:
                          session['Shoppingcart'] = MergeDicts(session['Shoppingcart'], DictItems)
                          return redirect(request.referrer)

              else:
                    session['Shoppingcart'] = DictItems
                    return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

@app.route('/carts')
def getCart():
    customer = None

    if 'customer' in session:
        customer = session["customer"]

    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
    grandtotal = "{:,.2f}".format(subtotal)

    return render_template('products/carts.html', customer=customer, grandtotal=grandtotal, displayBrands=displayBrands(), displayCategories=displayCategories())

@app.route('/updatecart/<int:code>', methods=['POST'])
def UpdateCart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method =="POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key , item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))

@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key , item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))
        
@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)