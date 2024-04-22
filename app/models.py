import secrets 
from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    tasks = db.relationship('Task', back_populates='author')
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone=True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, plaintext_pass):
        self.password = generate_password_hash(plaintext_pass)
        self.save()

    def check_password(self, plaintext_pass):
        return check_password_hash(self.password, plaintext_pass)
    
    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "dateCreated": self.date_created
        }

    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(tzinfo=timezone.utc) > now + timedelta(minutes=1): # if a user has a token and it doesn't expire in the next minute, then they'll get back the same token, else a new one
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1) #for the next hour, this token will be valid 
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}



class Task(db.Model):
    #DB Table setup 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    dueDate = db.Column(db.String, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # RE-ADD NULLABLE=FALSE 
    author = db.relationship('User', back_populates='tasks')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save() # NOT AUTO-SAVING WHEN TASK IS CREATED-- DEBUG NEEDED 

    def __repr__(self):
        return f"<Task {self.id}|{self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    # To transfer Task Object into a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "dueDate": self.dueDate,
            "createdAt": self.createdAt,
            "author": self.author.to_dict()  
        }