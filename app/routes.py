from app import app, models
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm

@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', title="Login", form=form)