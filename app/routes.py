from app import app
from app.models import Store, Assessment, Question, Response, Answer
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

@app.route('/stores')
def stores():
    stores = Store.query.all()
    return render_template("stores_dashboard.html", stores=stores)

@app.route('/stores/<int:store_id>')
def store_page(store_id):
    store = Store.query.get_or_404(store_id)
    return render_template("store_page.html", store=store)

@app.route('/stores/<int:store_id>/<int:assessment_id>')
def assessment_page(store_id, assessment_id):
    store = Store.query.get_or_404(store_id)
    assessment = Assessment.query.get_or_404(assessment_id)
    return render_template("assessment.html", assessment=assessment)
