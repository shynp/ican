from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo


class LoginForm(Form):
    email = StringField('Email',
                        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')

class ForgotPasswordForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	submit = SubmitField('Send Email for Password Reset')

class ResetPasswordForm(Form):
	new_password = PasswordField('Password', validators=[Required(), EqualTo('confirm_password', message='Passwords must match')])
	confirm_password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Reset Password')