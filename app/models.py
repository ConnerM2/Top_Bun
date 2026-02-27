from datetime import date, datetime, timezone, tzinfo
from typing import Optional
from zoneinfo import ZoneInfo
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Store(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    
    #This is a soft delete so you don't loose history
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True, index=True)


    responses = db.relationship("Response", backref='Store', cascade="all, delete-orphan", passive_deletes=True)

class Assessment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) #so.Mapped[int] is a 'type hint' which tells python what type an attribute is
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    questions = db.relationship("Question", backref='assessment', cascade="all, delete-orphan", passive_deletes=True) 

class Response(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    assessment_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Assessment.id), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now())
    report_month: so.Mapped[int] = so.mapped_column(sa.Integer, index=True, default=0)
    # Change report month nullable to True and just set default to 0, I want the user to be able to enter the month/ year
    yes_count: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    question_count: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    percent_score: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    form_type: so.Mapped[str] = so.mapped_column(sa.String(16), index=True)
    store_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Store.id, ondelete="CASCADE"), index=True)
    answers = db.relationship("Answer", backref="responses", cascade="all, delete-orphan", passive_deletes=True)
    assessment = db.relationship("Assessment")

    __table_args__ = (sa.UniqueConstraint("store_id", "assessment_id", "form_type", "report_month", name="uq_response_store_form_month"),)

    def calculate_score(self):
        total = 0
        score = 0

        for answer in self.answers:
            if answer.question and answer.question.question_type == "yes_no":
                total += 1
                if (answer.answer or "").strip().lower() == "yes":
                    score += 1
        if total == 0:
            self.percent_score = 0.0
        elif total > 0:
            self.question_count = total
            self.yes_count = score
            self.percent_score = (score / total) * 100

class Question(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    assessment_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Assessment.id, ondelete="CASCADE"), index=True)
    question_type: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    question: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True, index=True)
    position: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    score_aggregation: so.Mapped[str] = so.mapped_column(sa.String(64), server_default="ranked", nullable=False) #This allows us to specify how we want the quesiton to be totaled.

    answers = db.relationship("Answer", backref="question", cascade="all, delete-orphan", passive_deletes=True)

class Answer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Links answer to the specific submission (Response)
    response_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Response.id, ondelete="CASCADE"), index=True)

    # Links the answer to the specific question
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Question.id), index=True)
    answer: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True) 
