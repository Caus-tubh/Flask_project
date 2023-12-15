from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from store.auth import login_required
from store.models import db,Inventory,Product,Cart,Transaction,User
from store.browse import check_status
from datetime import datetime

bp = Blueprint('cart', __name__, url_prefix="/cart")

def generate_total(username):
    lis = db.session.execute(db.select(Cart.quantity, Cart.price)
                       .where(Cart.cart_user == User.user_id)
                       .where(User.name == username)).all()
    total =0 
    for i in lis:
        print(i, "+++++++++")
        total += i.quantity * i.price
    return total
def generate_carts():
    if g.user is not None:
        #print(g.user)
        cartlist = db.session.execute(db.select(Cart)
                            .where(Cart.cart_user == g.user.user_id)).scalars()
        #print(cartlist)
        return cartlist
    else:
        flash('please login to add to cart')
        return redirect(url_for('auth.login'))
    
@bp.route('/add',methods=['POST'])
@login_required
def method_name():
    try:
        product_name    = request.form['product_name']
        old_quantity = db.session.execute(db.select(Product.quantity)
                                .where(Product.product_name == product_name)).scalar()
        if old_quantity == 0:
            flash('product temporarily out of stock')
            return redirect(url_for('browse.index'))
        product_info    = db.session.execute(db.select(Product.product_name,Product.quantity,Product.price,Product.category)
                                            .where(Product.product_name == product_name)).one()
        quality         = db.session.execute(db.select(Inventory.category_quality)
                                            .where(Inventory.category_name == product_info.category)).scalar()
        #print(quality)
        if quality == 'solid':
            unit='Rs./Kg'
        if quality == 'liquid':
            unit = 'Rs./Litre'
        return render_template('cart/add.html',product_info = product_info,unit = unit)
    except Exception as e:
        flash(e)
        return redirect(url_for('cart.method_name'))

@bp.route('/buy/<product_name>',methods=['POST','GET'])
def buy(product_name):
    quantity = float(request.form['quantity'])
    amount   = request.form['price_per_unit']
    old_quantity = db.session.execute(db.select(Product.quantity)
                             .where(Product.product_name == product_name)).scalar()
    
    new_quantity = old_quantity-quantity 
    if new_quantity>=0:
        try:
            db.session.execute(db.update(Product)
                                .where(Product.product_name == product_name)
                                .values(quantity = new_quantity))
            cart = Cart(price=amount,quantity=quantity,product_name=product_name)
            g.user.CARTS.append(cart)
            db.session.add(g.user)
            db.session.commit()
        except Exception as e:
            flash(e)
            return redirect(url_for('browse.index'))
        else:
            db.session.commit()
            return redirect(url_for('browse.index'))
    else:
        flash('please select less tha or equal to product stock')
        return redirect(url_for('browse.index'))

@bp.route('/remove/<int:cart_id>',methods = ['POST'])
def remove_cart(cart_id):
    try:    
        product_name = request.form['product_name']
        user = db.session.execute(db.select(User.name)
                                .where(Cart.cart_user == User.user_id)).scalar()
        cart_quantity = db.session.execute(db.select(Cart.quantity)
                                .where(Cart.cart_id == cart_id)).scalar()
        old_quantity = db.session.execute(db.select(Product.quantity)
                                .where(Product.product_name == product_name)).scalar()
        new_quantity = old_quantity + cart_quantity
        cart = db.session.execute(db.select(Cart)
                             .where(Cart.cart_id == cart_id)).scalar()
        db.session.execute(db.update(Product)
                             .where(Product.product_name == product_name)
                             .values(quantity = new_quantity))
        db.session.delete(cart)
        db.session.commit()
    except Exception as e:
        flash(e)
        return url_for('browse.index')
    else:
        db.session.commit()
        return redirect(url_for('browse.index', username = user)) 
    
@bp.route('/your_cart/<username>',methods=['GET'])
def your_cart(username):
    total = generate_total(username)
    cartlist = generate_carts()
    return render_template('cart/your_cart.html', cartlist = cartlist, 
                                                username = username,
                                                total = total)

@bp.route('/checkout', methods=['POST'])
def checkout():
    try:
        transaction_name = datetime.now()
        username = request.form['customer']
        user_carts = db.session.execute(db.select(Cart)
                         .where(Cart.cart_user == User.user_id)
                         .where(User.name == username)).scalars()
        for cart in user_carts:
            trans_category = db.session.execute(db.select(Product.category)
                                          .where(cart.product_name == Product.product_name)).scalar()
            new_transaction = Transaction(  trans_product   = cart.product_name,
                                            trans_quantity  = cart.quantity,
                                            trans_price     = cart.price,
                                            trans_user      = cart.cart_user,
                                            trans_name      = transaction_name,
                                            trans_category  = trans_category)
            db.session.add(new_transaction)
            db.session.delete(cart)
            db.session.commit()
    except Exception as e:
        flash(e)
        redirect(url_for('cart.checkout'))
    else:
        db.session.commit()
        return redirect(url_for('browse.index'))