from . import db
from datetime import datetime, timezone
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __set_password(self, plaintext_pass):
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