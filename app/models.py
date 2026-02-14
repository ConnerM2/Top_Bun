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

    answers = db.relationship("Answer", backref="question")

class Answer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    response_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Response.id, ondelete="CASCADE"), index=True)
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Question.id), index=True)
    answer: so.Mapped[str] = so.mapped_column(sa.String(64))
