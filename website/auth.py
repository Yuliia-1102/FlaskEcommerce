from flask import Blueprint, render_template, flash, redirect, send_from_directory, request
from werkzeug.utils import secure_filename

from .forms import LoginForm, SignUpForm, PasswordChangeForm, ProfilePhotoForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer) # Зберігає ID користувача в сесії, Flask-Login запам'ятовує
                return redirect('/')
            else:
                flash('Invalid password!', 'danger')
        else:
            form.email.data = ''
            flash('Account does not exist. Please sign up.', 'danger')

    return render_template('login.html', form=form)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:
            new_customer = Customer()
            new_customer.username = username
            new_customer.email = email
            new_customer.password = password2 # хешування паролю

            existing_email = Customer.query.filter_by(email=email).first()
            existing_username = Customer.query.filter_by(username=username).first()

            if existing_email:
                form.email.data = ''
                flash('This email is already registered. Try another one.', 'danger')
            if existing_username:
                form.username.data = ''
                flash('This username is already taken. Choose a different one.', 'danger')

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect('/login')
            except Exception as e:
                print(e)
                if not existing_email or not existing_username:
                    print('Something went wrong. Account not created.')

        else:
            flash('Passwords do not match. Please try again.', 'danger')

    return render_template('signup.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@auth.route('/profile_photo/<path:filename>')
def get_image(filename):
    return send_from_directory('../profile_photo', filename)

@auth.route('/profile/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def profile(customer_id):
    customer_update_photo = Customer.query.get(customer_id)
    form = ProfilePhotoForm()

    if form.validate_on_submit():
       file = form.profile_pic.data
       file_name = secure_filename(file.filename)
       file_path = f'./profile_photo/{file_name}'
       file.save(file_path)

       try:
            Customer.query.filter_by(id=customer_id).update(dict(profile_pic = file_path))
            db.session.commit()
            return render_template('profile.html', customer=customer_update_photo, form=form)
       except Exception as e:
            print(e)
            flash('Profile picture is not updated!', 'danger')
    else:
        if request.method == "POST":
            flash('Profile picture is not updated!', 'danger')

    return render_template('profile.html', customer=customer_update_photo, form=form)

@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Your password has been updated.', 'success')
                return redirect(f'/profile/{customer_id}')
            else:
                flash('Your new passwords do not match.', 'danger')
        else:
            flash('Invalid current password.', 'danger')

    return render_template('change_password.html', form=form)