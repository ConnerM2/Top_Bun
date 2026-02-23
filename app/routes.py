from werkzeug.wrappers import response
from app import app, db
from app.models import Store, Assessment, Question, Response, Answer
from flask import render_template, flash, redirect, url_for, request,abort, jsonify
from app.forms import LoginForm, AssessmentForm, AddStoreForm, ArchiveForm, AddQuestionForm, ArchiveQuestions, SelectForm, MonthYearForm, AssessmentSelectForm
from wtforms import StringField
from sqlalchemy import engine, func
from datetime import date, datetime


def get_month_year_choices():
    """Last 12 months as (value, label), e.g. ('2026-02', 'Feb 2026'). Auto-updates with current date."""
    today = date.today()
    year, month = today.year, today.month
    choices = []
    for _ in range(12):
        d = date(year, month, 1)
        choices.append((d.strftime('%Y-%m'), d.strftime('%b %Y')))
        if month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
    return choices

@app.context_processor
def get_stores():
    stores = Store.query.all()
    stores = {'stores': stores}
    return stores

@app.route('/')
def index():
    return render_template('index.html', title="Top Bun")

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', title="Login", form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = MonthYearForm()
    form.month_year.choices = get_month_year_choices()
    my_date = date.today().replace(day=1)  # default: current month
    if form.validate_on_submit():
        value = form.month_year.data  # e.g. '2026-02'
        if value:
            y, m = int(value[:4]), int(value[5:7])
            my_date = date(y, m, 1)
    elif request.method == 'GET' and not form.month_year.data:
        form.month_year.data = my_date.strftime('%Y-%m')  # preselect current month
    responses = Response.query.filter(Response.report_month == my_date).all()
    stores = Store.query.filter_by(is_active=True).all()
    active_store_ids = []
    for store in stores:
        active_store_ids.append(store.id) # Stores on active store id's

    EVAL2_ASSESSMENT_ID = 2
    # eval2_first_question = Question.query.filter_by(assessment_id=EVAL2_ASSESSMENT_ID, is_active=True).order_by(Question.position).first()
    # eval2_q1_by_store = {}
    # if eval2_first_question:
    #     for r in responses:
    #         if r.assessment_id != EVAL2_ASSESSMENT_ID:
    #             continue
    #         for ans in r.answers:
    #             if ans.question_id == eval2_first_question.id and ans.answer:
    #                 eval2_q1_by_store[r.store_id] = ans.answer
                    # break

    eval2_questions = Question.query.filter_by(assessment_id=EVAL2_ASSESSMENT_ID, is_active=True).order_by(Question.position).all()
    eval2_scores_by_store = {}
    for r in responses:
        if r.assessment_id != EVAL2_ASSESSMENT_ID:
            continue
        for ans in r.answers:
            if ans.question_id not in eval2_scores_by_store:
                eval2_scores_by_store[ans.question_id] = {}
            if ans.answer is not None:
                eval2_scores_by_store[ans.question_id][r.store_id] = ans.answer
            
        print(eval2_scores_by_store)

    day_score_by_store = {}
    for r in responses:
        if r.form_type == "day" and r.store_id in active_store_ids and r.assessment_id != EVAL2_ASSESSMENT_ID: #either add a new form type for eval2 or add a check that checks if response if eval2. I got a random 0 in day collumn
            day_score_by_store[r.store_id] = r.percent_score

    night_score_by_store = {}
    for r in responses:
        if r.form_type == "night" and r.store_id in active_store_ids != EVAL2_ASSESSMENT_ID:
            night_score_by_store[r.store_id] = r.percent_score

    online_score_by_store = {}
    for r in responses:
        if r.form_type == "online" and r.store_id in active_store_ids != EVAL2_ASSESSMENT_ID:
            online_score_by_store[r.store_id] = r.percent_score


    def rank_calculator(score_by_store):
        sorted_score = dict(sorted(score_by_store.items(), key=lambda item: item[1], reverse=True))
        rank_by_store = {}
        rank = 10
        current_score = None
        tie_count = 0
        for store in sorted_score:
            if sorted_score[store] == 0:
                rank_by_store[store] = 0
            elif current_score == sorted_score[store]:
                rank_by_store[store] = rank
                tie_count += 1
            else:
                current_score = sorted_score[store]
                rank -= tie_count
                rank_by_store[store] = rank
                tie_count = 1
        return rank_by_store

    day_rank = rank_calculator(day_score_by_store)
    night_rank = rank_calculator(night_score_by_store)
    online_rank = rank_calculator(online_score_by_store)

    eval2_rank = {}
    for question in eval2_scores_by_store:
        eval2_rank[question] = rank_calculator(eval2_scores_by_store[question])
    
    

    print(eval2_rank)


    
    return render_template(
        "dashboard.html",
        responses=responses,
        stores=stores,
        date=my_date,
        form=form,
        day_rank=day_rank,
        night_rank=night_rank,
        online_rank=online_rank,
        eval2_rank=eval2_rank,
        eval2_questions=eval2_questions,
    )

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
        return redirect(url_for('index'))
    return render_template("add_store.html", form=form)

@app.route('/stores/<int:store_id>', methods=["GET", "POST"])
def store_page(store_id):
    store = Store.query.get_or_404(store_id)
    select_form = SelectForm()
    select_form.month_year.choices = get_month_year_choices()
    select_form.assessments.choices = [(a.id, a.name) for a in Assessment.query.all()]
    #drop down menus have two options. (value: what is sent to backend, label: what the user sees)

    if select_form.validate_on_submit():
        form_type = select_form.form_type.data
        assessment_id = select_form.assessments.data
        value = select_form.month_year.data
        if value:
            y, m = int(value[:4]), int(value[5:7])
            my_date = date(y, m, 1)

        return redirect(url_for('assessment_page', store_id=store.id, form_type=form_type, assessment_id=assessment_id, my_date=my_date))

    
    archive = ArchiveForm()
    if archive.validate_on_submit():
        store.is_active = False
        db.session.commit()
        flash("Deleted store")
        return redirect(url_for('index'))
    
    return render_template("store_page.html", store=store, archive=archive, select_form=select_form)

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
    form_type = request.args.get('form_type')
    date = request.args.get('my_date')
    assessment = db.session.get(Assessment, assessment_id)
    
    questions = Question.query.filter_by(is_active=True, assessment_id=assessment.id).order_by(Question.position).all()
    form = AssessmentForm()

    if form.validate_on_submit():
        response = Response(assessment_id=assessment.id, store_id=store.id, form_type=form_type, report_month=date)
        db.session.add(response)
        try:
            db.session.commit()
            flash("Response created successfully", "success")
            for question in questions:
                if question.question_type == "yes_no":
                    yes_no = request.form.get(f'question_{question.id}')
                    if yes_no == None:
                        answer_text = 'No'
                    else:
                        answer_text = 'Yes'
                elif question.question_type == "text":
                    answer_text = request.form.get(f'question_{question.id}')
                elif question.question_type == "score":
                    answer_text = request.form.get(f'question_{question.id}')
                else:
                    answer_text = request.form.get(f'question_{question.id}')
                if answer_text:
                    answer = Answer(response_id=response.id, question_id=question.id, answer=answer_text)
                    db.session.add(answer)
            response.calculate_score()
            db.session.commit()
            flash('Assessment submitted successfully!')
            return redirect(url_for('store_page', store_id=store_id))
        except:
            db.session.rollback()
            flash("Error: response already created for this store and time")
            print('excpet went off')
            return redirect(url_for('store_page', store_id=store_id))

    return render_template("assessment.html", assessment=assessment, store=store, form=form, questions=questions)

@app.route('/assessment', methods=["GET", "POST"])
def view_assessment():
    # Use assessment_id from URL so selection persists across redirects and refreshes
    assessment_id = request.args.get('assessment_id', type=int)
    if assessment_id is not None:
        assessment = db.session.get(Assessment, assessment_id)
        if assessment is None:
            assessment_id = None
    if assessment_id is None:
        assessment = Assessment.query.first()
        if assessment is not None:
            assessment_id = assessment.id

    select_ass = AssessmentSelectForm()
    select_ass.choice_assessment.choices = [(a.id, a.name) for a in Assessment.query.all()]
    if select_ass.validate_on_submit():
        # User chose a different assessment from dropdown — redirect so URL has it
        new_id = select_ass.choice_assessment.data
        return redirect(url_for("view_assessment", assessment_id=new_id))

    # Keep dropdown showing the current assessment
    if assessment is not None:
        select_ass.choice_assessment.data = assessment.id

    questions = Question.query.filter_by(assessment_id=assessment.id, is_active=True).order_by(Question.position).all() if assessment else []
    form = ArchiveQuestions()

    if form.validate_on_submit():
        question_id = request.form.get('question_id')
        question = Question.query.get_or_404(question_id)
        question.is_active = False
        question.position = 0
        db.session.commit()
        return redirect(url_for("view_assessment", assessment_id=assessment.id))
    return render_template("view_assessment.html", assessment=assessment, questions=questions, form=form, select_ass=select_ass)

@app.route('/assessment/<int:assessment_id>/add_question', methods=["GET", "POST"])
def add_question(assessment_id):
    assessment = db.session.get(Assessment, assessment_id)
    max_position = db.session.query(func.max(Question.position)).filter(Question.assessment_id == assessment.id).scalar()
    form = AddQuestionForm()

    if form.validate_on_submit():
        q_type = request.form.get('question_type')
        q = request.form.get('question')
        position = (max_position or 0) + 1
        question = Question(assessment_id=assessment.id, question_type=q_type, question=q, position=position)
        db.session.add(question)

        db.session.commit()
        flash("New question added!")
        return redirect(url_for('view_assessment', assessment_id=assessment.id))
    return render_template("add_question.html", form=form, assessment=assessment)

@app.route("/update-order", methods=["POST"])
def update_order():
    data = request.get_json()

    for item in data:
        question = Question.query.get(item["id"])
        question.position = item["position"]

    db.session.commit()
    return jsonify({"status": "success"})
