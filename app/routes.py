from app import app, db
from app.models import Store, Assessment, Question, Response, Answer
from flask import render_template, flash, redirect, url_for, request,abort
from app.forms import LoginForm, AssessmentForm, AddStoreForm, DeleteForm
from wtforms import StringField

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

@app.route('/stores/add_store', methods=["GET", "POST"])
def add_store():
    form = AddStoreForm()
    if form.validate_on_submit():
        location = request.form.get('location')
        if location:
            store = Store(location=location)
            db.session.add(store)
        db.session.commit()
        flash('New Store Added')
        return redirect(url_for('stores'))
    return render_template("add_store.html", form=form)

@app.route('/stores/<int:store_id>', methods=["GET", "POST"])
def store_page(store_id):
    store = Store.query.get_or_404(store_id)
    assessment = Assessment.query.first()
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(store)
        db.session.commit()
        flash("Deleted store")
        return redirect(url_for('stores'))
    
    return render_template("store_page.html", store=store, assessment=assessment, form=form)

@app.route('/stores/<int:store_id>/res<int:response_id>')
def view_response(store_id, response_id):
    store = Store.query.get_or_404(store_id)
    response = Response.query.get_or_404(response_id)

    if response.store_id != store_id:
        abort(404)

    assessment = response.assessment

    return render_template("response.html", response=response, strore=store, assessment=assessment)

@app.route('/stores/<int:store_id>/<int:assessment_id>', methods=["GET", "POST"])
def assessment_page(store_id, assessment_id):
    store = Store.query.get_or_404(store_id)
    assessment = Assessment.query.get_or_404(assessment_id)

    form = AssessmentForm()

    if form.validate_on_submit():
        response = Response(assessment_id=assessment.id, store_id=store.id)
        db.session.add(response)
        db.session.flush()

        for question in assessment.questions:
            answer_text = request.form.get(f'question_{question.id}')
            if answer_text:
                answer = Answer(response_id=response.id, question_id=question.id, answer=answer_text)
                db.session.add(answer)
        db.session.commit()
        flash('Assessment submitted successfully!')
        return redirect(url_for('store_page', store_id=store_id))

    return render_template("assessment.html", assessment=assessment, store=store, form=form)
