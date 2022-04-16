from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileRequired, FileAllowed, FileField

class CustomerRegisterForm(Form):
    name = StringField('Name: ', [validators.DataRequired()])
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired(), validators.EqualTo('password', message='Both password must match!')])

    profile = FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'], 'Image only please')])
    submit = SubmitField('Register')

class CustomerLoginFrom(Form):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])