from flask import flash, render_template, redirect, url_for, \
    current_app, request
from ..models import User
from .forms import LoginForm, ForgotPasswordForm, ResetPasswordForm
from . import main
from .. import db
from flask.ext.login import login_user, logout_user, login_required
import datetime
import random
import string
from ..email import send_email


def random_string(length):
    pool = string.letters + string.digits
    return ''.join(random.choice(pool) for i in xrange(length))

@main.route('/')
@main.route('/index')
def index():
    return render_template('main/landing.html')

@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    app = current_app._get_current_object()
    form = ResetPasswordForm(CSRF_ENABLED=app.config['WTF_CSRF_ENABLED'])
    reset_id = request.args.get('id')
    user = User.query.filter_by(password_reset_id=reset_id).first()
    if user is not None and user.password_reset_valid:
        if form.validate_on_submit():
            if user.password_reset_time - datetime.datetime.now() < datetime.timedelta(1, 0, 0):
                user.password = form.new_password.data
                user.password_reset_valid = False
                db.session.add(user)
                db.session.commit()
                flash('Password reset successful!')
                return redirect(url_for('.login'))
            else:
                user.password_reset_valid = False
                db.session.add(user)
                db.session.commit()
                flash('Sorry, you did not reset your password within 24 hours. Please try again')
                return redirect(url_for('.forgot_password'))
    else:
        flash('Sorry, you are not allowed to access this page')
        return redirect(url_for('.login'))
    return render_template('main/reset_password.html', form=form)

@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    app = current_app._get_current_object()
    form = ForgotPasswordForm(CSRF_ENABLED=app.config['WTF_CSRF_ENABLED'])
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            hash_id = random_string(32)
            user.password_reset_id = hash_id
            user.password_reset_valid = True
            user.password_reset_time = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()
            send_email(form.email.data, 'Reset iCAN Password',
                'email/reset_password', root_url=request.url_root, reset_id=hash_id)
            flash('We have sent a reset link to your email. Please use it to reset your password!')
            return redirect(url_for('.login'))
        else:
            flash('The email you entered is not valid')
    return render_template('main/forgot_password.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    app = current_app._get_current_object()
    form = LoginForm(CSRF_ENABLED=app.config['WTF_CSRF_ENABLED'])
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if user.is_role("admin"):
                return redirect(url_for('admin.index'))
            elif user.is_role("student"):
                return redirect(url_for('students.index'))
            else:
                return redirect(url_for('mentors.index'))
        flash('Invalid username or password.')
    return render_template('main/login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.index'))

