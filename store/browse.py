from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from store.auth import login_required
from store.models import db,Inventory,Product,Cart,Product_search
from sqlalchemy import or_

bp = Blueprint('browse', __name__)

def generate_list(*args):
    if len(args)==0:
        lis = db.session.execute(db.select(Inventory.category_name)).all()
        return lis
    if args[0]=='default':
        lis = db.session.execute(db.select(Product)).scalars()
        #print(lis)
        return lis
    if len(args)==1:
        lis = db.session.execute(db.select(Product)
                        .where(Product.category == args[0])).scalars()
        #print(lis)
        return lis
    
def check_status():
    login_status = True
    if g.user == None:
        login_status = False
    #print(login_status,"+++++++++++++++++++++++++++++++++++++++")
    return login_status
@bp.route('/<string:category>')
def cat(category):
    return redirect(url_for('browse.browse', category = category))

@bp.route('/',methods=['GET','POST'])
def index():
    login_status = check_status()
    lis = generate_list()
    if login_status == False:
        manager_status = 0
        username =None
    else:
        manager_status = g.user.manager
        username       = g.user.name
    itemlist = generate_list('default')
    #print(login_status)
    return render_template("index.html", status         = login_status, 
                                         list           = lis, 
                                         manager_status = manager_status,
                                         itemlist       = itemlist,
                                         username       = username)

@bp.route('/browse/<category>',methods=['GET','POST'])
def browse(category):
    login_status = check_status()
    lis = generate_list()
    if login_status == False:
        manager_status = 0
        username =None
    else:
        manager_status = g.user.manager
        username        = g.user.name
    itemlist = generate_list(category)
    
    return render_template("index.html",status          = login_status, 
                                        list            = lis, 
                                        category        = category,
                                        manager_status  = manager_status,
                                        itemlist        = itemlist,
                                        username        = username)

@bp.route('/search',methods=['POST','GET'])
def search():
    q = request.form['search']
    #print(type(q))
    if '=' in q:
        #print('working')
        q = q.replace('=', ':')
    #print(q)
    login_status = check_status()
    lis = generate_list()
    if login_status == False:
        manager_status = 0
        username =None
    else:
        manager_status = g.user.manager
        username        = g.user.name
    itemlist = Product_search.query.filter(or_(
        Product_search.product_name.op('MATCH')(q),     
        Product_search.description.op('MATCH')(q),  
        Product_search.price.op('MATCH')(q),        
        Product_search.supplier.op('MATCH')(q),     
        Product_search.expirey_date.op('MATCH')(q), 
        Product_search.category.op('MATCH')(q))).all()
    print(itemlist,'++++++++++++++++++++++++')
    return render_template('search.html',status         = login_status,
                                        list           = lis, 
                                        manager_status = manager_status,
                                        itemlist       = itemlist,
                                        username       = username,
                                        search         = q)