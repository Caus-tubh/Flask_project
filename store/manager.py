from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, 
    current_app
)
from werkzeug.exceptions import abort
from store.auth import login_required
from store.models import db,Inventory,Product,Transaction
from datetime import date
from werkzeug.utils import secure_filename
import os

bp = Blueprint('manager', __name__, url_prefix='/manager')

@bp.route('/product/', methods=['GET','POST'])
def no_category_selected():
    flash('select a category first')
    return redirect(url_for('browse.index'))

@bp.route('/category', methods=['GET','POST'])
def category():
    try:
        if request.method =="GET":
            return render_template('manager/category.html')
        if request.method =="POST":
            categoryname = request.form['category_name']
            if request.form['action']=='add':
                if request.form['quality']=='liquid':
                    quality='liquid'
                else:
                    quality='solid'
                new_category = Inventory(category_name = categoryname,category_quality = quality)
                db.session.add(new_category)
                db.session.commit()
    except Exception as e:
        flash(e)
        return render_template('manager/category.html')
    else:
        return redirect(url_for('browse.index'))
            
@bp.route('/category/edit',methods=['GET','POST'])
def edit():
    try:
        if request.method =='GET':
            categories = db.session.execute(db.select(Inventory.category_name)).all()
            return render_template('manager/edit.html', categories = categories)
        if request.method == 'POST':
            old_category = request.form['old_category_name']
            new_category = request.form['new_category_name']
            quality      = request.form['quality']
            db.session.execute(db.update(Inventory)
                                .where(Inventory.category_name == old_category)
                                .values(category_name = new_category,category_quality = quality)
                                )
            db.session.execute(db.update(Product)
                                .where(Product.category == old_category)
                                .values(category = new_category)
                                )
    except Exception as e:
        flash(e)
        return render_template('manager/category.html')
    else:
            #print('SUCCESS')
        db.session.commit()
        return redirect(url_for('browse.index'))
        
@bp.route('/category/delete',methods=['POST'])
def delete_category():
    category=request.form['category']
    products_of_category = db.session.execute(db.select(Product)
                                                .where(Product.category == category)).first()
    #print(products_of_category,'+++++++++++++++++++++++++++++')
    if products_of_category == None:
        old_category = db.session.execute(db.select(Inventory)
                                                .where(Inventory.category_name == category)).scalar()
        db.session.delete(old_category)
        db.session.commit()
        return redirect(url_for('browse.index'))
    else:
        flash('cant delete category if there are products in it')
        return redirect(url_for('browse.index'))
        
@bp.route('/product/<category>', methods=['GET','POST'])
def product(category):
    if request.method =="GET":
        return render_template('manager/product.html', category = category)
    if request.method =="POST":
        try:
            my_img = request.files['product_image']
            filename = secure_filename(request.form['product_name']+'.jpg') 
            my_img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            expirey = date.fromisoformat(request.form['expirey'])
            if request.form['action']=='add':
                    curr_category = db.session.execute(db.select(Inventory)
                                                        .where(Inventory
                                                        .category_name == category)
                                                    ).scalar_one_or_none()
                    new_product = Product(  product_name = request.form['product_name'],
                                        price        = request.form['price'],
                                        description  = request.form['description'],
                                        supplier     = request.form['supplier'],
                                        expirey_date = expirey,
                                        quantity     = request.form['quantity'])
                    curr_category.PRODUCT.append(new_product)
                    db.session.add(curr_category)
        except Exception as e:
            db.session.rollback()
            flash('Make sure every form value is filled')
            return render_template('manager/product.html', category = category)
        else:
            db.session.commit()
            return redirect(url_for('browse.browse',category = category))
            
@bp.route('/product/edit/<edit_product>', methods=['GET','POST'])
def edit_product(edit_product):
    if request.method=='GET':
        product = db.session.execute(db.select(Product)
                                        .where(Product.product_name == edit_product)).scalar()
        db.session.commit()
        return render_template('manager/edit_product.html', product = product)
    if request.method=='POST':
        try:
            if request.files['product_image']:
                my_img = request.files['product_image']
                filename = secure_filename(request.form['product_name']+'.jpg') 
                my_img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            expirey = date.fromisoformat(request.form['expirey'])
            db.session.execute(db.update(Product)
                                .where(Product.product_name == edit_product)
                                .values(product_name = request.form['product_name'],
                                        price        = request.form['price'],
                                        description  = request.form['description'],
                                        supplier     = request.form['supplier'],
                                        expirey_date = expirey,
                                        quantity     = request.form['quantity']))      
        except Exception as e:
            flash(e)
            return redirect(url_for('browse.index'))
        else:
            db.session.commit()
            return redirect(url_for('browse.index'))

@bp.route('/product/delete/<product_name>', methods=['GET'])
def delete_product(product_name):
    try:
        delete = db.session.execute(db.select(Product).where(Product.product_name == product_name)).scalar()
        db.session.delete(delete)
        db.session.commit()
    except Exception as e:
        flash(e)
        redirect(url_for('browse.index'))
    else:
        return redirect(url_for('browse.index'))