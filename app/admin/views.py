import datetime

from . import admin
from ..models import User, University, GeneralTask, FAQ, Task
from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from forms import ReassignForm, EditTaskForm, TaskCreationForm, EditFAQForm, FAQCreationForm, EditUniversityForm, CreateUniversityForm, EditMentorForm, EditProfileForm
from ..decorators import admin_required
from ..email import send_text

from flask.ext.login import login_required, current_user

@admin.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin.route('/mentors')
@login_required
@admin_required
def mentors():
    mentors = User.query.filter_by(user_role="mentor").all()
    # print(mentors[0].id)
    universities = University.query.all()
    for i in range(len(mentors)):
        uni_id = mentors[i].university_id - 1 or 0
        mentors[i].university_name = universities[uni_id].name
    return render_template('admin/mentors.html', mentors=mentors)

@admin.route('/mentors/edit/<mentor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_mentor(mentor_id):
    mentor = User.query.filter_by(id=mentor_id).first()
    form = EditMentorForm(obj=mentor)
    uni_id = mentor.university_id - 1 or 0
    university_choices = [(u.id,u.name) for u in University.query.all()]
    university_choices[uni_id], university_choices[0] = university_choices[0], university_choices[uni_id]
    form.university.choices = university_choices
    if form.validate_on_submit():
        mentor.name = form.name.data
        mentor.email = form.email.data
        mentor.phone = form.phone.data
        mentor.university_id = form.university.data
        db.session.add(mentor)
        db.session.commit()
        flash("Edited data for " + mentor.name)
        return redirect(url_for('.mentors'))
    return render_template('admin/edit_mentor.html', mentor=mentor, form=form)

@admin.route('/mentors/delete/<mentor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_mentor(mentor_id):
    GeneralTask.query.filter_by(user_id=mentor_id).delete()
    User.query.filter_by(id=mentor_id).delete()
    db.session.commit()
    return redirect(url_for('.mentors'))

@admin.route('/students')
@login_required
@admin_required
def students():
    students = User.query.filter_by(user_role="student").all()
    universities = University.query.all()
    for i in range(len(students)):
        uni_id = students[i].university_id - 1 or 0
        students[i].university_name = universities[uni_id].name
    return render_template('admin/students.html', students=students)

@admin.route('/reassign/<student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reassign(student_id):
    form = ReassignForm()
    student = User.query.get(student_id)
    form.mentor.choices = [(m.id,m.name) for m in User.query.filter_by(user_role="mentor").all()]
    university_choices = [(u.id,u.name) for u in University.query.all()]
    uni_id = student.university_id - 1 or 0
    university_choices[uni_id], university_choices[0] = university_choices[0], university_choices[uni_id]
    form.university.choices = university_choices
    if form.validate_on_submit():
        mentor = User.query.get(form.mentor.data)
        student.mentor = mentor
        student.university_id = form.university.data
        db.session.add(student)
        db.session.commit()
        flash("Reassigned " + student.name)
        return redirect(url_for('.students'))

    return render_template('admin/reassign.html', form=form, student=student)

@admin.route('/students/delete/<student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_student(student_id):
    GeneralTask.query.filter_by(user_id=student_id).delete()
    User.query.filter_by(id=student_id).delete()
    db.session.commit()
    return redirect(url_for('.students'))

@admin.route('/universities')
@login_required
@admin_required
def universities():
    universities = University.query.all()
    return render_template('admin/universities.html', universities=universities)

@admin.route('/universities/edit/<university_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_universities(university_id):
    university = University.query.filter_by(id=university_id).first()
    form = EditUniversityForm(obj=university)
    if form.validate_on_submit():
        description = form.description.data
        university.description = description
        db.session.add(university)
        db.session.commit()
        flash("Edited description for " + university.name)
        return redirect(url_for('.index'))
    return render_template('admin/edit_universities.html', university=university, form=form)

@admin.route('/universities/add_university', methods=['GET', 'POST'])
@login_required
@admin_required
def render_add_university_form():
    form = CreateUniversityForm()
    if form.validate_on_submit():
        universityTest = University.query.filter_by(name=form.name.data).first()
        if not universityTest:
            university = University(name=form.name.data,
                                    description=form.description.data)
            db.session.add(university)
            db.session.commit()
            universities = University.query.all()
            return redirect(url_for('.universities'))
        else:
            flash("A university by this name already exists")
            return redirect(url_for('.render_add_university_form'))
    return render_template('/admin/add_university.html', form=form)

@admin.route('/tasks')
@login_required
@admin_required
def tasks():
    tasks = GeneralTask.query.all()
    return render_template('admin/tasks.html', tasks=tasks)

@admin.route('/tasks/edit/<task_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_task(task_id):
    task = GeneralTask.query.get(task_id)
    form = EditTaskForm(obj=task)
    uni_id = task.university_id - 1 or 0
    university_choices = [(u.id,u.name) for u in University.query.all()]
    university_choices[uni_id], university_choices[0] = university_choices[0], university_choices[uni_id]
    form.university.choices = university_choices
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.university_id = form.university.data
        db.session.add(task)
        db.session.commit()
        flash("Successfully edited task")
        return redirect(url_for('.index'))
    return render_template('admin/edit_task.html', form=form)

@admin.route('/tasks/delete/<task_id>')
@login_required
@admin_required
def delete_task(task_id):
    task = GeneralTask.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Deleted task")
    return redirect(url_for('.tasks'))

@admin.route('/tasks/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_task():
    form = TaskCreationForm()
    form.universities.choices = [(university.id, university.name) for university in University.query.all()]
    form.universities.choices.append((-1, "All"))
    if form.validate_on_submit():
        if -1 in form.universities.data:
            new_task = GeneralTask()
            new_task.title = form.title.data
            new_task.description = form.description.data
            new_task.deadline = form.deadline.data
            db.session.add(new_task)
            db.session.commit()
        else:
            for university in form.universities.data:
                new_task = GeneralTask()
                new_task.title = form.title.data
                new_task.description = form.description.data
                new_task.deadline = form.deadline.data
                new_task.university_id = university
                db.session.add(new_task)
                db.session.commit()
        flash("Successfully created task")
        return redirect(url_for(".tasks"))
    return render_template('admin/create_task.html', form=form)

@admin.route('/faqs')
@login_required
@admin_required
def faqs():
    faqs = FAQ.query.all()
    for faq in faqs:
        uni_ids = faq.get_universities()
        uni_names = []
        for uni_id in uni_ids:
            uni = University.query.filter_by(id=uni_id).first()
            if uni:
                uni_names.append(str(uni.name))
        faq.university_names = uni_names
    return render_template('admin/faqs.html', faqs=faqs)

@admin.route('/faqs/edit/<faq_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    form = EditFAQForm(obj=faq)
    form.universities.choices = [(university.id, university.name) for university in University.query.all()]
    form.universities.choices.append((-1, "All"))
    uni_ids = faq.get_universities()

    if form.validate_on_submit():
        faq.question = form.question.data
        faq.answer = form.answer.data

        print(form.universities.data)
        if -1 in form.universities.data:
            university_ids = [university.id for university in University.query.all()]
        else:
            university_ids = []
            for uni_id in form.universities.data:
                uni = University.query.filter_by(id=uni_id).first()
                if uni:
                    university_ids.append(uni_id)
        faq.set_universities(university_ids)

        db.session.add(faq)
        db.session.commit()
        flash("Successfully edited FAQ")
        return redirect(url_for('.faqs'))

    form.universities.data = uni_ids

    return render_template('admin/edit_faq.html', form=form)

@admin.route('/faqs/delete/<faq_id>')
@login_required
@admin_required
def delete_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash("Deleted FAQ")
    return redirect(url_for('.faqs'))

@admin.route('/faqs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_faq():
    form = FAQCreationForm()
    form.universities.choices = [(university.id, university.name) for university in University.query.all()]
    form.universities.choices.append((-1, "All"))

    if form.validate_on_submit():
        new_faq = FAQ()
        new_faq.question = form.question.data
        new_faq.answer = form.answer.data

        if -1 in form.universities.data:
            university_ids = [university.id for university in University.query.all()]
        else:
            university_ids = []
            for uni_id in form.universities.data:
                uni = University.query.filter_by(id=uni_id).first()
                if uni:
                    university_ids.append(uni_id)
        new_faq.set_universities(university_ids)

        db.session.add(new_faq)
        db.session.commit()
        flash("Successfully created FAQ")
        return redirect(url_for(".faqs"))
    return render_template('admin/create_faq.html', form=form)


@admin.route('/send_reminders')
def send_reminders():
    for student in User.query.filter_by(user_role="student").all():
        tasks = student.tasks.filter_by(completed=False).order_by(Task.deadline).all()
        for task in tasks:
            deadline_now_diff = task.deadline - datetime.datetime.now()
            if deadline_now_diff < datetime.timedelta(1):
                send_text(student.phone, "Hello there! " + task.title + " is due in less than 24 hours!")
    return 'Reminders sent.'

@admin.route('/edit-admin-account', methods=['GET', 'POST'])
@login_required
@admin_required
def profile_edit():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        if form.new_password.data and form.current_password:
            if current_user.verify_password(form.current_password.data):
                current_user.password = form.new_password.data
                db.session.add(current_user)
                db.session.commit()
                flash('Your profile has been updated')
            else:
                flash('Invalid current password; password not updated')
        else:
            db.session.add(current_user)
            db.session.commit()
            flash('Your profile email has been updated')
        return redirect(url_for('.index'))
    form.email.data = current_user.email
    return render_template('admin/profile-edit.html', student=current_user,
                           form=form)

