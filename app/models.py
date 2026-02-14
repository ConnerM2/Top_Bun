from datetime import datetime, timezone
from typing import Optional
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
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    questions = db.relationship("Question", backref='assessment', cascade="all, delete-orphan", passive_deletes=True)

class Response(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    assessment_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Assessment.id), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    store_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Store.id, ondelete="CASCADE"), index=True)

    answers = db.relationship("Answer", backref="responses", cascade="all, delete-orphan", passive_deletes=True)
    assessment = db.relationship("Assessment")

class Question(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    assessment_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Assessment.id, ondelete="CASCADE"), index=True)
    question_type: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    question: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True, index=True)
    position: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)

    answers = db.relationship("Answer", backref="question", cascade="all, delete-orphan", passive_deletes=True)


class Answer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Links answer to the specific submission (Response)
    response_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Response.id, ondelete="CASCADE"), index=True)

    # Links the answer to the specific question
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Question.id), index=True)
    answer: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
