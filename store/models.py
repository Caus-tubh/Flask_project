from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
Base = declarative_base()
db = SQLAlchemy()
class User(db.Model):
    __tablename__   = 'users'
    user_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name            = db.Column(db.String, nullable=False, unique=True)
    password        = db.Column(db.String, nullable=False)
    manager         = db.Column(db.Boolean, nullable=False)
    CARTS           = db.relationship('Cart')
    TRANSACTION     = db.relationship('Transaction')

class Inventory(db.Model):
    __tablename__   = 'inventory'
    category_id     = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_name   = db.Column(db.String, unique=True, nullable=False)
    category_quality= db.Column(db.String)
    PRODUCT         = db.relationship("Product", back_populates = "CATEGORY")
    
class Product(db.Model):
    __tablename__   = 'products'
    product_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name    = db.Column(db.String, unique=True, nullable=False)
    description     = db.Column(db.String, nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    supplier        = db.Column(db.String, nullable=False)
    expirey_date    = db.Column(db.Date, nullable=False)
    category        = db.Column(db.String, db.ForeignKey("inventory.category_name"))
    quantity        = db.Column(db.Integer, nullable=False)
    CATEGORY        = db.relationship("Inventory", back_populates = "PRODUCT")

class Cart(db.Model):
    __tablename__   = 'carts'
    cart_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name    = db.Column(db.String, nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    quantity        = db.Column(db.Integer, nullable=False)
    cart_user       = db.Column(db.String, db.ForeignKey("users.user_id"))

class Transaction(db.Model):
    __tablename__   = 'transactions'
    transaction_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trans_product   = db.Column(db.String)
    trans_quantity  = db.Column(db.Integer)
    trans_price     = db.Column(db.Integer)
    trans_name      = db.Column(db.DateTime)
    trans_category  = db.Column(db.String)
    trans_user      = db.Column(db.Integer, db.ForeignKey("users.user_id"))

class Product_search(db.Model):
    __tablename__   = 'product_search'
    rowid           = db.Column(db.Integer, primary_key=True)
    product_name    = db.Column(db.String, unique=True, nullable=False)
    description     = db.Column(db.String, nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    supplier        = db.Column(db.String, nullable=False)
    expirey_date    = db.Column(db.Date, nullable=False)
    category        = db.Column(db.String, nullable=False)
    quantity        = db.Column(db.Integer, nullable=False)
