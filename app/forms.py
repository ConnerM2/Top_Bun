from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
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

class ArchiveForm(FlaskForm):
    submit = SubmitField("Archive")

class ArchiveQuestions(FlaskForm):
    submit = SubmitField("Archive")

class AddQuestionForm(FlaskForm):
    question_type = SelectField('Question Type', choices=[("yes_no", "Check Box"), ('score', 'Extra score')], validators=[DataRequired()])
    question = StringField("Question", validators=[data_required()])
    category = SelectField('Category', choices=[("Outside", "Outside"), ("Front of Store", "Front of Store")])
    submit = SubmitField("Add Question")

class SelectForm(FlaskForm):
    form_type = SelectField('Form Type', choices=[('day', 'Day'), ('night', 'Night'), ('online', 'Online')])
    assessments = SelectField('Assessment', choices=[], validators=[DataRequired()])
    month_year = SelectField('Month', choices=[], validators=[DataRequired()])
    submit = SubmitField("Select Form")

class AssessmentSelectForm(FlaskForm):
    choice_assessment = SelectField('Assessments', choices=[], validators=[DataRequired()])
    submit = SubmitField("Go")

class MonthYearForm(FlaskForm):
    """Month/year dropdown - choices are set in the view to last 12 months."""
    month = SelectField('Month', choices=[('01', 'Jan'),('02', 'Feb'),('03', 'Mar'),('04', 'April'),('05', 'May'),('06', 'June'),('07', 'July'),('08', 'Aug'),('09', 'Sep'),('10', 'Oct'),('11', 'Nov'),('12', 'Dec'),], validators=[DataRequired()])
    year = SelectField('Year', choices=[], validators=[DataRequired()])
    submit = SubmitField("Go")
