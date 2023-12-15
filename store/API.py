from flask_restful import Resource, marshal_with, marshal
from store.models import db, Product, User, Inventory
from store.API_validate import product, user, category, ApiResponse
from store.API_validate import ValueError, InternalError, InputError
from store.API_validate import parser, product_parser, product_subparser
from datetime import date
from flask import request, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from io import BytesIO
from PIL import Image
import json

def product_maker(product_object,inventory_object):
    product={}
    category={}
    category['category_name'] = inventory_object.category_name
    category['quality'] = inventory_object.category_quality
    product['product_id'] = product_object.product_id
    product['price'] = product_object.price
    product['quantity'] = product_object.quantity
    product['product_name'] = product_object.product_name
    product['description'] = product_object.description
    product['supplier'] = product_object.supplier
    product['expirey_date'] = product_object.expirey_date
    product['category'] = category
    return product

class product_API(Resource):
    @marshal_with(product)
    def post(self):
        try:
            args = product_parser.parse_args()
            category_args = product_subparser.parse_args(req=args)
            product_name  = args.get("product_name",None) 
            description   = args.get("description",None) 
            price         = args.get("price",None) 
            supplier      = args.get("supplier",None) 
            expirey_date  = args.get("expirey_date",None) 
            quantity      = args.get("quantity",None) 
            category_name = category_args.get("category_name", None)
            expirey = date.fromisoformat(expirey_date)
            
            new_product = Product(product_name = product_name,
                                    price        = price,
                                    description  = description,
                                    supplier     = supplier,
                                    expirey_date = expirey,
                                    quantity     = quantity)                
            curr_category = db.session.execute(db.select(Inventory)
                                                            .where(Inventory
                                                            .category_name == category_name)
                                                        ).scalar_one_or_none()
        except:
            raise InputError(402)
        curr_category.PRODUCT.append(new_product)
        db.session.add(curr_category)
        db.session.commit()
        result = product_maker(new_product, curr_category)
        return result
    @marshal_with(product)
    def put(self,product_name):
        try:
            args = product_parser.parse_args()
            category_args = product_subparser.parse_args(req=args)
            product_id    = args.get("product_id",None)  
            product_name  = args.get("product_name",None) 
            description   = args.get("description",None) 
            price         = args.get("price",None) 
            supplier      = args.get("supplier",None) 
            expirey_date  = args.get("expirey_date",None) 
            quantity      = args.get("quantity",None) 
            category_name = category_args.get("category_name", None)
            category_quality = category_args.get("category_quality", None)
            expirey = date.fromisoformat(expirey_date)
        except:
            raise InputError(402)
        try:
            db.session.execute(db.update(Product).where(Product.product_id==product_id)
                                                .values(product_name = product_name,
                                                        price        = price,
                                                        description  = description,
                                                        supplier     = supplier,
                                                        expirey_date = expirey,
                                                        quantity     = quantity,
                                                        category     = category_name))
            curr_product = db.session.execute(db.select(Product)
                            .where(Product.product_id==product_id)
                            ).scalar_one_or_none()  
            curr_category = db.session.execute(db.select(Inventory)
                                                            .where(Inventory
                                                    .category_name == category_name)
                                                        ).scalar_one_or_none()  
        except:
            raise ValueError(404)  
        db.session.commit()
        result = product_maker(curr_product,curr_category)
        return result
    
    @marshal_with(product)
    def get(self,product_name):
        #print(request.headers)
        print(request.view_args['product_name'])
        #product_name = request.view_args['product_name']
        curr_product = db.session.execute(db.select(Product).where(Product.product_name==product_name)).scalar_one_or_none()
        if curr_product:
            try:
                curr_category = db.session.execute(db.select(Inventory)
                                                            .where(Inventory
                                                    .category_name == curr_product.category)
                                                        ).scalar_one_or_none()    
                result = product_maker(curr_product,curr_category)
                return result
            except:
                raise InternalError(500)
        else:
            raise ValueError(status_code=404)
    @marshal_with(ApiResponse)
    def delete(self,product_name):
        #print(request.headers)
        #print(request.view_args['product_name'])
        #product_name = request.view_args['product_name']
        curr_product = db.session.execute(db.select(Product).where(Product.product_name==product_name)).scalar_one_or_none()
        if curr_product:
            print(curr_product)
            db.session.delete(curr_product)
            db.session.commit() 
            ApiResponse['code'] = 200
            ApiResponse['message'] = 'succesful!'
            return ApiResponse
        else:
            raise InputError(402)
        
    
    def post(self,product_name):
        #print(request.headers)
        try:
            image_data = BytesIO(request.data)
            my_img = Image.open(image_data)
            my_img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], str(product_name)+'.jpg'))
            ApiResponse = {}
            ApiResponse['code'] = 200
            ApiResponse['message'] = 'succesful!'
            return ApiResponse
        except:
            InputError(402)

class inventory_API(Resource):
    @marshal_with(category)
    def post(self):
        try:
            args = parser.parse_args()
            category_name  = args.get('category_name', None)
            quality = args.get('quality', None)
            new_category = Inventory(category_name = category_name,category_quality = quality)
            db.session.add(new_category)
            db.session.commit()
        except:
            raise InputError(402)
        else:
            category = {}
            category['category_name'] = category_name
            category['quality'] = quality
            return category
        
    def put(self,category_name):
        args = parser.parse_args()
        try:
            old_category = category_name
            new_category = args.get('category_name', None)
            quality      = args.get('quality', None)
            db.session.execute(db.update(Inventory)
                                .where(Inventory.category_name == old_category)
                                .values(category_name = new_category,category_quality = quality)
                                )
        except:
            raise InputError(402)
        category = {}
        category['category_name'] = category_name
        category['quality'] = quality
        return category 
    def get(self,category_name):
        try:
            List = db.session.execute(db.select(Product.product_name)
                                       .where(Product.category == category_name)).scalars()
        except:
            raise ValueError(404)
        ans = {}
        #print(ans,'+++++++++++++++')
        ans['products_in_category'] = []
        #print(ans,'---------------')
        for i in List:
            ans['products_in_category'].append(i)    
        return ans
    @marshal_with(ApiResponse)
    def delete(self,category_name):
        try:
            category=category_name
            products_of_category = db.session.execute(db.select(Product)
                                                .where(Product.category == category)).first()
            if products_of_category == None:
                old_category = db.session.execute(db.select(Inventory)
                                                .where(Inventory.category_name == category)).scalar()
                db.session.delete(old_category)
                db.session.commit()
            else:
                raise ValueError(404)
        except:
            raise InternalError(500)
        res = {}
        res['code'] = 200
        res['message'] = "Success!" 
        return res
    
class user_API(Resource):
    @marshal_with(user)
    def post(self):    
        args = parser.parse_args()
        username   = args.get("name",None)  
        password  = args.get("password",None) 
        manager   = args.get("manager",None)
        new_user = User(name = username, password = generate_password_hash(password), manager = manager)
        db.session.add(new_user)
        db.session.commit()
        session.clear()
        session['user_id'] = new_user.user_id
    
        you = {}
        you['username'] = username
        you['password'] = password
        you['manager'] = manager
        return you