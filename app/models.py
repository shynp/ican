from . import db, login_manager
from flask import request
from flask.ext.login import UserMixin, login_required
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    user_role = db.Column(db.String(15))
    phone = db.Column(db.String(10), unique=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'))
    mentor = db.relationship('User', backref='students', remote_side=[id])
    bio = db.Column(db.Text)
    tasks = db.relationship('Task', backref='student', lazy='dynamic')
    display_phone = db.Column(db.Boolean) # for mentors only, True: display phone & email; False: display just email
    avatar_hash = db.Column(db.String(32))
    password_reset_id = db.Column(db.String(32))
    password_reset_time = db.Column(db.DateTime)
    password_reset_valid = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # add mentor matching and task addition here

    def __repr__(self):
        return '<User %r>' % self.name

    def is_role(self, role):
        return self.user_role == role

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def match_with_mentor(self):
        '''
        Matches self(role=student) with User(role=mentor)
        1) Tries to match based on shared university
        2) If student.university is None or university.mentors is None:
            matches student with any mentor with fewest students
        '''
        university = self.university
        possible_mentors = []
        if university:
            possible_mentors = [m for m in university.users if m.user_role == 'mentor']
        if (university is None or len(possible_mentors) == 0):
            #possible_mentors = [m for m in User.query.all() if m.user_role == 'mentor']
            possible_mentors = User.query.filter_by(user_role='mentor').all()
        if (len(possible_mentors) >= 1):
            min_mentor = possible_mentors[0]
            min_students = len(possible_mentors[0].students)
            for m in possible_mentors:
                if len(m.students) < min_students:
                    min_students = len(m.students)
                    min_mentor = m
            self.mentor = min_mentor

    def get_all_tasks_list(self):
        studentList = self.students
        taskList = []
        for student in studentList:
            taskList += student.tasks.all()
        taskList.sort(key=lambda r: r.deadline)
        return taskList


    def add_task(self, description, deadline, title):
        '''
        Adds task to list of student tasks in order of deadline from closest -> furthest
        so tasks are already sorted when they are displayed
        '''
        new_task = Task(deadline=deadline, description=description, user_id=self.id, title=title)
        self.tasks.append(new_task)
        db.session.add(self)
        db.session.add(new_task)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id

    def complete_task(self):
        self.completed = True
        db.session.add(self)
        db.session.commit()

    def uncomplete_task(self):
        self.completed = False
        db.session.add(self)
        db.session.commit()


class GeneralTask(db.Model):
    __tablename__ = 'general_tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'))


class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    tasks = db.relationship('GeneralTask', backref='university')
    users = db.relationship('User', backref='university')
    description = db.Column(db.String(5000))


class FAQ(db.Model):
    __tablename__ = 'FAQs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
