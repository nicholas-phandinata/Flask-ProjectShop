from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField

class RegistrationForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.DataRequired(), validators.Length(min=6, max=35), 
            validators.Email()])
    password = PasswordField('New Password', [validators.DataRequired(),
               validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
        username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
        password = PasswordField('Password', [validators.DataRequired()])

class VerifyForm(Form):
        otp = IntegerField('OTP', [validators.DataRequired()])