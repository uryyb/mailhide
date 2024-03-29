from mailhide import db, helpers
from sqlalchemy.orm import relationship
import bcrypt

# the user table structure 
class DBUser(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return "<DBUser %r>" % self.username

class Emails(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    db_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(320), unique=False, nullable=False)
    email_hash = db.Column(db.String(40), unique=True, nullable=False)

def setup_db():
    db.create_all()
    user_dict = {
        "admin": DBUser(username="admin", email="admin@example.com", password=bcrypt.hashpw(b"abc123", bcrypt.gensalt())),
        "guest": DBUser(username="guest", email="guest@example.com", password=bcrypt.hashpw(b"password", bcrypt.gensalt()))
    }
    for key, user in user_dict.items():
        print("%s added to the database."% user.username)
        db.session.add(user)
    db.session.commit()

    u = DBUser(id=1)
    email_dict = {
        "email": Emails(email="email@example.com", email_hash=helpers.hash_email("email@example.com"), db_user_id=u.id),
        "jsmith": Emails(email="jsmith@example.com", email_hash=helpers.hash_email("jsmith@example.com"), db_user_id=u.id)
    }
    
    for key, email in email_dict.items():
        print("%s added to the database."% email.email)
        db.session.add(email)
    db.session.commit()