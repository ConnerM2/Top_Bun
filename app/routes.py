from app import app, db
from app.models import Store, Assessment, Question, Response, Answer
from flask import render_template, flash, redirect, url_for, request,abort
from app.forms import LoginForm, AssessmentForm, AddStoreForm, ArchiveForm, AddQuestionForm, ArchiveQuestions
from wtforms import StringField
from sqlalchemy import func

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
    assessment = Assessment.query.first() #Add a check to see if assessment exists
    form = ArchiveForm()
    if form.validate_on_submit():
        store.is_active = False
        db.session.commit()
        flash("Deleted store")
        return redirect(url_for('stores'))
    
    return render_template("store_page.html", store=store, assessment=assessment, form=form)

@app.route('/stores/<int:store_id>/res<int:response_id>')
def view_response(store_id, response_id):
    store = Store.query.get_or_404(store_id)
    response = Response.query.get_or_404(response_id)
    answers = response.answers

    if response.store_id != store_id:
        abort(404)

    assessment = response.assessment
    questions = Question.query.filter_by(assessment_id=assessment.id).order_by(Question.position).all()
    answers_dict = {answer.question_id: answer for answer in answers}

    return render_template("response.html", response=response, store=store, assessment=assessment, questions=questions, answers_dict=answers_dict)

@app.route('/stores/<int:store_id>/<int:assessment_id>', methods=["GET", "POST"])
def assessment_page(store_id, assessment_id):
    store = Store.query.get_or_404(store_id)
    assessment = Assessment.query.get_or_404(assessment_id)
    questions = Question.query.filter_by(is_active=True, assessment_id=assessment.id).order_by(Question.position).all()
    form = AssessmentForm()

    if form.validate_on_submit():
        response = Response(assessment_id=assessment.id, store_id=store.id)
        db.session.add(response)
        db.session.flush()

        for question in questions: 
            answer_text = request.form.get(f'question_{question.id}')
            if answer_text:
                answer = Answer(response_id=response.id, question_id=question.id, answer=answer_text)
                db.session.add(answer)
        db.session.commit()
        flash('Assessment submitted successfully!')
        return redirect(url_for('store_page', store_id=store_id))

    return render_template("assessment.html", assessment=assessment, store=store, form=form, questions=questions)

@app.route('/assessment', methods=["GET", "POST"])
def view_assessment():
    assessment = Assessment.query.first()
    questions = Question.query.filter_by(assessment_id=assessment.id, is_active=True).order_by(Question.position).all()
    # Using query allows you to use filter_by
    form = ArchiveQuestions()

    if form.validate_on_submit():
        question_id = request.form.get('question_id')
        question = Question.query.get_or_404(question_id)
        question.is_active = False
        question.position = 0
        db.session.commit()
        return redirect(url_for("view_assessment"))
    return render_template("view_assessment.html", assessment=assessment, questions=questions, form=form)

@app.route('/assessment/add_question', methods=["GET", "POST"])
def add_question():
    assessment = Assessment.query.first()
    max_position = db.session.query(func.max(Question.position)).filter(Question.assessment_id == assessment.id).scalar()
    form = AddQuestionForm()

    if form.validate_on_submit():
        q_type = request.form.get('question_type')
        q = request.form.get('question')
        position = (max_position or 0) + 1
        question = Question(assessment_id=1, question_type=q_type, question=q, position=position)
        db.session.add(question)

        db.session.commit()
        flash("New question added!")
        return redirect(url_for('view_assessment'))
    return render_template("add_question.html", form=form, assessment=assessment)
