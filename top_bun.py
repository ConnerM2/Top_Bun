from app import app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import Store, Assessment, Question, Response, Answer

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Store': Store, "Assessment": Assessment, "Question": Question, "Response": Response, "Answer": Answer}

