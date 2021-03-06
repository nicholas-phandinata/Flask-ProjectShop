from email.policy import default
from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import app, mysql, photos
from .forms import Addproducts
import secrets, os, math

min_threshold = 1
max_threshold = 7

def displayBrands():
      cur = mysql.connection.cursor()
      cur.execute("SELECT DISTINCT(P.Brand_Id) Brand_Id, B.Name FROM Products P JOIN Brands B ON P.Brand_Id = B.Brand_Id")
      displayBrands = cur.fetchall()
      return displayBrands

def displayCategories():
      cur = mysql.connection.cursor()
      cur.execute("SELECT DISTINCT(P.Cat_Id) Cat_Id, C.Name FROM Products P JOIN Categories C ON P.Cat_Id = C.Cat_Id")
      displayCategories = cur.fetchall()
      return displayCategories

@app.route('/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/page/<int:page>', methods=['GET', 'POST'])
def home(page):
      customer = None

      if 'customer' in session:
        customer = session["customer"]

      limit = 6
      offset = page*limit - limit

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Products WHERE Stock > 0")
      total_row = cur.rowcount
      total_page = math.ceil(total_row / limit)
      next_page = page + 1
      prev_page = page - 1
      current_page = page

      global min_threshold, max_threshold

      if current_page == max_threshold and current_page != total_page:
            min_threshold += 5
            max_threshold += 5
      elif current_page == min_threshold and current_page != 1:
            min_threshold -= 5
            max_threshold -= 5
      elif current_page == 1:
            min_threshold = 1
            max_threshold = 7
      elif current_page == total_page:
            for x in range(7,10000,5):
                  if current_page <= x:
                        min_threshold = x - 6
                        max_threshold = x
                        break

      cur.execute("SELECT * FROM Products WHERE Stock > 0 LIMIT %s OFFSET %s", (limit,offset))
      displayProducts =  list(cur.fetchall())
      for i, x in enumerate(displayProducts):
            displayProducts[i] = list(displayProducts[i])
            rupiah = "{:,.2f}".format(x[2])
            displayProducts[i][2] = rupiah

      q = request.form.get('searchInput')
      if q:
            cur = mysql.connection.cursor()
            qs = "%" + q + "%"
            cur.execute("SELECT * FROM Products WHERE Name LIKE %s", [qs])
            displayProducts =  list(cur.fetchall())

            if not displayProducts:
                  searchNotFound = "snf"
                  return render_template('products/index.html', customer=customer, searchNotFound=searchNotFound, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)
            
            for i, x in enumerate(displayProducts):
                  displayProducts[i] = list(displayProducts[i])
                  rupiah = "{:,.2f}".format(x[2])
                  displayProducts[i][2] = rupiah

            searchFound = "sf"
            return render_template('products/index.html', customer=customer, searchFound=searchFound, displayProducts=displayProducts, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)

      return render_template('products/index.html', customer=customer, displayProducts=displayProducts, displayBrands=displayBrands(), displayCategories=displayCategories(), total_page=total_page, next_page=next_page, prev_page=prev_page, current_page=current_page, max_threshold=max_threshold, min_threshold=min_threshold)

@app.route('/product/<int:id>')
def single_page(id):
      customer = None

      if 'customer' in session:
        customer = session["customer"]

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Products WHERE Product_Id = %s", [id])
      product = list(cur.fetchone())
      rupiah = "{:,.2f}".format(product[2])
      product[2] = rupiah

      return render_template('products/single_page.html', customer=customer, product=product, displayBrands=displayBrands(), displayCategories=displayCategories())

@app.route('/brand/<int:id>', methods=['GET', 'POST'])
def get_brand(id):
      customer = None

      if 'customer' in session:
        customer = session["customer"]

      page = request.args.get('page', 1, type=int)
      limit = 6
      offset = page*limit - limit

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Products WHERE Brand_Id = %s AND Stock > 0", [id])
      total_row = cur.rowcount
      total_page = math.ceil(total_row / limit)
      next_page = page + 1
      prev_page = page - 1
      current_page = page

      global min_threshold, max_threshold

      if current_page == max_threshold and current_page != total_page:
            min_threshold += 5
            max_threshold += 5
      elif current_page == min_threshold and current_page != 1:
            min_threshold -= 5
            max_threshold -= 5
      elif current_page == 1:
            min_threshold = 1
            max_threshold = 7
      elif current_page == total_page:
            for x in range(7,10000,5):
                  if current_page <= x:
                        min_threshold = x - 6
                        max_threshold = x
                        break

      cur.execute("SELECT * FROM Products WHERE Brand_Id = %s AND Stock > 0 LIMIT %s OFFSET %s", (id,limit,offset))
      displayProductsByBrand = list(cur.fetchall())
      for i, x in enumerate(displayProductsByBrand):
            displayProductsByBrand[i] = list(displayProductsByBrand[i])
            rupiah = "{:,.2f}".format(x[2])
            displayProductsByBrand[i][2] = rupiah
      
      q = request.form.get('searchInput')
      if q:
            cur = mysql.connection.cursor()
            qs = "%" + q + "%"
            cur.execute("SELECT * FROM Products WHERE Brand_Id = %s AND Name LIKE %s", (id, qs))
            displayProducts =  list(cur.fetchall())
            
            if not displayProducts:
                  searchNotFound = "sn"
                  return render_template('products/index.html', customer=customer, searchNotFound=searchNotFound, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)
            
            for i, x in enumerate(displayProducts):
                  displayProducts[i] = list(displayProducts[i])
                  rupiah = "{:,.2f}".format(x[2])
                  displayProducts[i][2] = rupiah

            searchFound = "sf"
            return render_template('products/index.html', customer=customer, searchFound=searchFound, displayProducts=displayProducts, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)

      return render_template('products/index.html', customer=customer, id=id, displayProductsByBrand=displayProductsByBrand, displayBrands=displayBrands(), displayCategories=displayCategories(), total_page=total_page, next_page=next_page, prev_page=prev_page, current_page=current_page, max_threshold=max_threshold, min_threshold=min_threshold)

@app.route('/category/<int:id>', methods=['GET', 'POST'])
def get_category(id):
      customer = None

      if 'customer' in session:
        customer = session["customer"]

      page = request.args.get('page', 1, type=int)
      limit = 6
      offset = page*limit - limit

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Products WHERE Cat_Id = %s AND Stock > 0", [id])
      total_row = cur.rowcount
      total_page = math.ceil(total_row / limit)
      next_page = page + 1
      prev_page = page - 1
      current_page = page

      global min_threshold, max_threshold

      if current_page == max_threshold and current_page != total_page:
            min_threshold += 5
            max_threshold += 5
      elif current_page == min_threshold and current_page != 1:
            min_threshold -= 5
            max_threshold -= 5
      elif current_page == 1:
            min_threshold = 1
            max_threshold = 7
      elif current_page == total_page:
            for x in range(7,10000,5):
                  if current_page <= x:
                        min_threshold = x - 6
                        max_threshold = x
                        break

      cur.execute("SELECT * FROM Products WHERE Cat_Id = %s AND Stock > 0 LIMIT %s OFFSET %s", (id,limit,offset))
      displayProductsByCategory = list(cur.fetchall())
      for i, x in enumerate(displayProductsByCategory):
            displayProductsByCategory[i] = list(displayProductsByCategory[i])
            rupiah = "{:,.2f}".format(x[2])
            displayProductsByCategory[i][2] = rupiah

      q = request.form.get('searchInput')
      if q:
            cur = mysql.connection.cursor()
            qs = "%" + q + "%"
            cur.execute("SELECT * FROM Products WHERE Cat_Id = %s AND Name LIKE %s", (id, qs))
            displayProducts =  list(cur.fetchall())
            if not displayProducts:
                  searchNotFound = "sn"
                  return render_template('products/index.html', customer=customer, searchNotFound=searchNotFound, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)
            
            for i, x in enumerate(displayProducts):
                  displayProducts[i] = list(displayProducts[i])
                  rupiah = "{:,.2f}".format(x[2])
                  displayProducts[i][2] = rupiah
            
            searchFound = "sf"
            return render_template('products/index.html', customer=customer, searchFound=searchFound, displayProducts=displayProducts, displayBrands=displayBrands(), displayCategories=displayCategories(), q=q)

      return render_template('products/index.html', customer=customer, id=id, displayProductsByCategory=displayProductsByCategory, displayBrands=displayBrands(), displayCategories=displayCategories(), total_page=total_page, next_page=next_page, prev_page=prev_page, current_page=current_page, max_threshold=max_threshold, min_threshold=min_threshold)

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
      if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
      if request.method=="POST":
            getbrand = request.form.get('brand')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Brands (Name) VALUES (%s)", [getbrand])
            mysql.connection.commit()
            cur.close()
            flash(f"The Brand {getbrand} was added to the database", "success")
            return redirect(url_for('addbrand'))
      return render_template('products/addbrand.html', brands="brands")

@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
      if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Brands WHERE Brand_Id = %s", [id])
      updatebrand = cur.fetchone()
      brand = request.form.get('brand')
      if request.method=="POST":
            update_query = "UPDATE Brands set Name = %s WHERE Brand_Id = %s"
            values = (brand, updatebrand[0])
            cur.execute(update_query,values)
            mysql.connection.commit()
            cur.close()
            flash(f'Your brand "{updatebrand[1]}" has been updated to "{brand}"', 'success')
            return redirect(url_for('brands'))
      return render_template('products/updatebrand.html', title='Update Brand Page', updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Brands WHERE Brand_Id = %s", [id])
      deletebrand = cur.fetchone()
      relatedproducts = cur.execute("SELECT Product_Id FROM Products WHERE Brand_Id = %s", [id])
      if request.method=="POST":
            if relatedproducts > 0:
                  datarelprod = cur.fetchall()
                  for x in datarelprod:
                        cur.execute("SELECT Image_1, Image_2, Image_3 FROM Products WHERE Product_Id = %s", [x[0]])
                        res = cur.fetchone()
                        img_1 = res[0]
                        img_2 = res[1]
                        img_3 = res[2]
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_1))
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_2))
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_3))
            cur.execute("DELETE FROM Brands WHERE Brand_Id = %s", [id])
            mysql.connection.commit()
            flash(f'The brand "{deletebrand[1]}" has been deleted', 'success')
            return redirect(url_for('brands'))
      flash(f'The brand "{deletebrand[1]}" cant be deleted', 'warning')
      return redirect(url_for('admin'))

@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
      if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
      if request.method=="POST":
            getcategory = request.form.get('category')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Categories (Name) VALUES (%s)", [getcategory])
            mysql.connection.commit()
            cur.close()
            flash(f"The Category {getcategory} was added to the database", "success")
            return redirect(url_for('addcat'))
      return render_template('products/addbrand.html')

@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
      if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Categories WHERE Cat_Id = %s", [id])
      updatecat = cur.fetchone()
      category = request.form.get('category')
      if request.method=="POST":
            update_query = "UPDATE Categories set Name = %s WHERE Cat_Id = %s"
            values = (category, updatecat[0])
            cur.execute(update_query,values)
            mysql.connection.commit()
            cur.close()
            flash(f'Your category "{updatecat[1]}" has been updated to "{category}"', 'success')
            return redirect(url_for('categories'))
      return render_template('products/updatebrand.html', title='Update Category Page', updatecat=updatecat)

@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Categories WHERE Cat_Id = %s", [id])
      deletecategory = cur.fetchone()
      relatedproducts = cur.execute("SELECT Product_Id FROM Products WHERE Cat_Id = %s", [id])
      if request.method=="POST":
            if relatedproducts > 0:
                  datarelprod = cur.fetchall()
                  for x in datarelprod:
                        cur.execute("SELECT Image_1, Image_2, Image_3 FROM Products WHERE Product_Id = %s", [x[0]])
                        res = cur.fetchone()
                        img_1 = res[0]
                        img_2 = res[1]
                        img_3 = res[2]
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_1))
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_2))
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_3))
            cur.execute("DELETE FROM Categories WHERE Cat_Id = %s", [id])
            mysql.connection.commit()
            flash(f'The category "{deletecategory[1]}" has been deleted', 'success')
            return redirect(url_for('categories'))
      flash(f'The category "{deletecategory[1]}" cant be deleted', 'warning')
      return redirect(url_for('admin'))

@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
      if 'username' not in session:
        flash(f"Please Log In First", 'danger')
        return redirect(url_for('login'))
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM Brands")
      brands = cur.fetchall()
      cur.execute("SELECT * FROM Categories")
      categories = cur.fetchall()
      cur.close()
      form = Addproducts(request.form)
      if request.method == "POST":
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            color = form.colors.data
            desc = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')
            image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

            cur = mysql.connection.cursor()
            sql_query = "INSERT INTO Products (Name, Price, Discount, Stock, Color, Description, Brand_Id, Cat_Id, Image_1, Image_2, Image_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (name, price, discount, stock, color, desc, brand, category, image_1, image_2, image_3)
            cur.execute(sql_query, values)
            mysql.connection.commit()
            cur.close()

            flash(f'The product {name} has been added to the database', 'success')
            return redirect(url_for('addproduct'))
      return render_template('products/addproduct.html', title="Add Product Page", form=form, brands=brands, categories=categories)

@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
      cur = mysql.connection.cursor()
      cur.execute("SELECT Products.*, Brands.Name, Categories.Name FROM Products JOIN Brands ON Products.Brand_Id = Brands.Brand_Id JOIN Categories ON Products.Cat_Id = Categories.Cat_Id WHERE Product_Id = %s", [id])
      updateproduct = cur.fetchone()
      cur.execute("SELECT * FROM Brands WHERE Brand_Id != %s", [updateproduct[8]])
      brands = cur.fetchall()
      cur.execute("SELECT * FROM Categories WHERE Cat_Id != %s", [updateproduct[9]])
      categories = cur.fetchall()
      form = Addproducts(request.form)
      if request.method == "POST":
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            color = form.colors.data
            desc = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')

            if request.files.get('image_1'):
                  try:
                        cur.execute("SELECT Image_1 FROM Products WHERE Product_Id = %s", [id])
                        img_1 = cur.fetchone()
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_1[0]))
                        img_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_1 = %s WHERE product_Id = %s"
                        val = (img_1, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()
                  except:
                        img_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_1 = %s WHERE product_Id = %s"
                        val = (img_1, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()

            if request.files.get('image_2'):
                  try:
                        cur.execute("SELECT Image_2 FROM Products WHERE Product_Id = %s", [id])
                        img_2 = cur.fetchone()
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_2[0]))
                        img_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_2 = %s WHERE product_Id = %s"
                        val = (img_2, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()
                  except:
                        img_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_2 = %s WHERE product_Id = %s"
                        val = (img_2, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()

            if request.files.get('image_3'):
                  try:
                        cur.execute("SELECT Image_3 FROM Products WHERE Product_Id = %s", [id])
                        img_3 = cur.fetchone()
                        os.unlink(os.path.join(current_app.root_path, "static/images/" + img_3[0]))
                        img_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_3 = %s WHERE product_Id = %s"
                        val = (img_3, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()
                  except:
                        img_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
                        upt_quer = "UPDATE Products set Image_3 = %s WHERE product_Id = %s"
                        val = (img_3, id)
                        cur.execute(upt_quer, val)
                        mysql.connection.commit()

            update_query = "UPDATE Products set Name = %s, Price = %s, Discount = %s, Stock = %s," \
                           "Color = %s, Description = %s, Brand_Id = %s, Cat_Id = %s WHERE Product_Id = %s"
            values = (name, price, discount, stock, color, desc, brand, category, id)
            cur.execute(update_query,values)
            mysql.connection.commit()
            cur.close()

            flash(f'The product "{updateproduct[1]}" has been successfully updated', 'success')
            return redirect(url_for('admin'))
      form.name.data = updateproduct[1]
      form.price.data = updateproduct[2]
      form.discount.data = updateproduct[3]
      form.stock.data = updateproduct[4]
      form.colors.data = updateproduct[5]
      form.description.data = updateproduct[6]
      return render_template('products/updateproduct.html', form=form, brands=brands, categories=categories, updateproduct=updateproduct)

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
      cur = mysql.connection.cursor()
      cur.execute("SELECT Image_1, Image_2, Image_3, Name FROM Products WHERE Product_Id = %s", [id])
      res = cur.fetchone()
      os.unlink(os.path.join(current_app.root_path, "static/images/" + res[0]))
      os.unlink(os.path.join(current_app.root_path, "static/images/" + res[1]))
      os.unlink(os.path.join(current_app.root_path, "static/images/" + res[2]))
      cur.execute("DELETE FROM Products WHERE Product_Id = %s", [id])
      mysql.connection.commit()
      flash(f'The product "{res[3]}" has been successfully deleted', 'success')
      return redirect(url_for('admin'))