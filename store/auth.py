from flask import render_template, flash, session, redirect, url_for, g, Response
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request, Blueprint
from store.models import db
from store.models import User,Inventory
from functools import wraps
bp = Blueprint('auth',__name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    #print(user_id,"+++++++++++++++++++++++")
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.execute(db.select(User).where(User.user_id == user_id)).scalar_one_or_none()


@bp.route('/login',methods=['GET'])
def login():
    return render_template("auth/login.html")

@bp.route('/verification',methods=['POST','GET'])
def verification():
    if request.method == "POST" and request.form['type']=='login':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username or not password:
            flash("Did not enter username and/or password")
            return render_template("auth/login.html")
        if error is None:
            user = db.session.execute(db.select(User).where(User.name == username)).scalar_one_or_none()
            correct_password = check_password_hash(user.password, password)
            if user is None:
                flash('username does not exist')
                return render_template("auth/login.html")
            if correct_password != True:
                flash('incorrect password')
                return render_template("auth/login.html")
            else:
                session.clear()
                session['user_id'] = user.user_id
                return redirect(url_for('browse.index'))
            
    if request.method == "POST" and request.form['type']=='register':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username or not password:
            flash("Did not enter username and/or password")
            return render_template("auth/login.html")
        if error is None:
            try:
                new_user = User(name = username, password = generate_password_hash(password), manager = 0)
                db.session.add(new_user)
                db.session.commit()
                session.clear()
                session['user_id'] = new_user.user_id
                return redirect(url_for('browse.index'))
            except Exception as e:
                flash("User already exists")
                return redirect(url_for('auth.login'))
        flash(error)

    return redirect(url_for('browse.index'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('browse.index'))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('please login')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
