from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import app, mysql

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
        rupiah = "{:,.2f}".format(product[2])
        product[2] = rupiah

        if product_id and quantity and color and request.method == "POST":
              DictItems = {product_id:{'name':product[1],'price':product[2],
              'discount':product[3],'color':color,'quantity':quantity,'image':product[10]}}

              if 'Shoppingcart' in session:
                    print(session['Shoppingcart'])
                    if product_id in session['Shoppingcart']:
                          print("This product is already in your cart")
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