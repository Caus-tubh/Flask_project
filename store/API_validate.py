from flask_restful import fields, reqparse
from datetime import date
from werkzeug.exceptions import HTTPException
from flask import make_response

class Onlydate(fields.Raw):
    def format(self, value):
        return str(value)

product_parser = reqparse.RequestParser()
product_subparser = reqparse.RequestParser()
product_parser.add_argument('product_name', type=str, required = True)
product_parser.add_argument('description', type=str, required = True)
product_parser.add_argument('supplier', type=str, required = True)
product_parser.add_argument('price', type=int, required = True)
product_parser.add_argument('category', type=dict, required = True)
product_parser.add_argument('quantity', type=int, required = True)
product_parser.add_argument('expirey_date', type=str, required = True)
product_parser.add_argument('product_id', type=int)

product_subparser.add_argument('category_name', type=str, location=('category',))
product_subparser.add_argument('category_quality', type=str, location=('category',))

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('password', type=str)
parser.add_argument('category_name', type=str)
parser.add_argument('quality', type=str)
parser.add_argument('manager', type=bool)

category = {
    'category_name' : fields.String,
    'quality'       : fields.String
}

product = {
        'product_id'     : fields.Integer,
        'product_name'   : fields.String,
        'description'    : fields.String ,
        'price'          : fields.Integer ,
        'supplier'       : fields.String ,
        'expirey_date'   : Onlydate,
        'quantity'       : fields.Integer,
        'category'       : fields.Nested(category)
}
user = {
    'user_id'  : fields.Integer,      
    'name'     : fields.String,
    'password' : fields.String,
    'manager'  : fields.Boolean 
}

ApiResponse = {
    'code' : fields.Integer,
    'type' : fields.String,
    'message' : fields.String
}

## exceptions ##

class ValueError(HTTPException):
    def __init__(self,status_code):
        self.response = make_response('value not found',status_code)

class InternalError(HTTPException):
    def __init__(self,status_code):
        self.response = make_response('Internal server error',status_code)

class InputError(HTTPException):
    def __init__(self,status_code):
        self.response =  make_response('Input value wrong',status_code)