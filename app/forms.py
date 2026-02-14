from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, data_required

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Sign In")

class AssessmentForm(FlaskForm):
    submit = SubmitField("Submit Assessment")

class AddStoreForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField("Add Store")