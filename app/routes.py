import sqlalchemy.exc
from flask import current_app as app
from flask import request, render_template, redirect, url_for
from .models import db, User, Email, Phone
from .forms import UserForm


@app.route('/')
def index():

    search = request.args.get('gsearch')

    if search:

        user = User.query.filter((User.username.ilike(f'%{search}%'))).distinct(User.username).group_by(User.username)
        page = request.args.get('page')
        if page and page.isdigit():
            page = int(page)
        else:
            page = 1
        pages = user.paginate(page=page, per_page=4)
        return render_template('show_all.html', pages=pages)
    else:
        return render_template('index.html')


@app.route('/create-user', methods=['GET', 'POST'])
def form_create_user():
    if request.method == 'POST':
        get_name = request.form.get('name')
        get_email = request.form.get('email')
        get_phone = request.form.get('phone')
        get_address = request.form.get('address')
        if get_name:
            try:
                user = User(username=get_name, address=get_address)
                db.session.add(user)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                return render_template('form.html', name='user already exist')
        else:
            return render_template('form.html', name=None)
        if get_email:
            email = Email(user_id=user.id, email=get_email)
            db.session.add(email)
        elif not get_email:
            email = Email(user_id=user.id, email=get_phone)
            db.session.add(email)

        if get_phone:
            phone = Phone(user_id=user.id, phone=get_phone)
            db.session.add(phone)
        elif not get_phone:
            phone = Phone(user_id=user.id, phone=get_phone)
            db.session.add(phone)
        db.session.commit()
        return render_template('form.html', name=get_name)

    return render_template('form.html', name=None)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST', 'DELETE'])
def edit_user(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    print(user)
    success = False
    if request.method == 'POST':
        print(request.form)
        form = UserForm(request.form, obj=user)
        form.populate_obj(user)
        db.session.commit()
        success = True
        return render_template('cart_edit.html', form=form, success=success)
    else:
        form = UserForm(obj=user)
        return render_template('cart_edit.html', form=form, success=success)


@app.route('/show-users', methods=['GET'])
def show_all_users():

    user = User.query.order_by(User.username)
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = user.paginate(page=page, per_page=4)

    return render_template('show_all.html', users=user, pages=pages)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



