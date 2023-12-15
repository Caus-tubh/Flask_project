from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, 
    current_app
)
from store.models import db, Transaction
from datetime import datetime, timedelta
from datetime import date as dt
import os
import csv
import matplotlib.pyplot as plt
import pandas as pd

bp = Blueprint('stats', __name__)

script_dir = os.path.dirname(__file__)
relative_file_path = os.path.join(script_dir, 'static','data', 'data.csv')
stats_file_path = os.path.join(script_dir, 'static','data','graphs')
def write():
    transactions = db.session.execute(db.select(Transaction)).scalars()
    with open(relative_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['product','quantity','price','name','category','user'])
        for transaction in transactions:
            data = []
            data.append(transaction.trans_product)
            data.append(transaction.trans_quantity)
            data.append(transaction.trans_price)
            data.append(transaction.trans_name)
            data.append(transaction.trans_category)
            data.append(transaction.trans_user)
            #print(data)
            writer.writerow(data)
        
@bp.route('/stats', methods = ['GET'])
def statistics():
    #now = dt.today()
    #dates = [now - timedelta(days=x) for x in range]
    write()
    data = pd.read_csv(relative_file_path)

    data["name"] = pd.to_datetime(data["name"])
    date = data["name"]
    quantity = data["quantity"]
    price = data["price"]
    category = data["category"]
    total = quantity * price

    fig, ax = plt.subplots(1,figsize=(12.5,5.5),squeeze=False,layout='constrained')
    ax[0,0].scatter(date, total, label='total')
    twin = ax[0,0].twinx()
    twin.scatter(date,quantity, label='quantity',color='g')
    ax[0,0].scatter(date,price, label='price')
    ax[0,0].set_xlabel('date')
    ax[0,0].set_ylabel('price')
    twin.set_ylabel('quantity',color='g')
    twin.tick_params(axis='y',labelcolor='g')
    twin.legend(loc='upper center')
    ax[0,0].legend(loc='best')
    ax[0,0].set_title('Volume of transactions')
    
    fig.savefig(os.path.join(stats_file_path, 'freq.jpg'))
    return render_template('stats.html')