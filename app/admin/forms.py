from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, StringField, TextField, DateField, widgets, SelectMultipleField, TextAreaField, PasswordField
from wtforms.validators import Required, Email, EqualTo

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ReassignForm(Form):
    mentor = SelectField('Which mentor do you want to assign them to', validators=[Required()], coerce=int)
    university = SelectField('Which university do you want to assign them to', validators=[Required()], coerce=int)
    submit = SubmitField('Reassign')

class EditTaskForm(Form):
    title = StringField('Task Title')
    description = TextField('Task Description')
    university = SelectField('Which college is this task for?', validators=[Required()], coerce=int)
    deadline = DateField('When is this task due? (YYYY-MM-DD)')
    submit = SubmitField('Update Task')

class TaskCreationForm(Form):
    universities = MultiCheckboxField("Universities", coerce=int)
    title = StringField('Task Title')
    description = TextField('Task Description')
    deadline = DateField('When is this task due? (YYYY-MM-DD)')
    submit = SubmitField('Create Task')

class EditFAQForm(Form):
    question = TextField('Question')
    answer = TextField('Answer')
    universities = MultiCheckboxField("Universities", coerce=int)
    submit = SubmitField('Update FAQ')

class FAQCreationForm(Form):
    question = TextField('Question')
    answer = TextField('Answer')
    universities = MultiCheckboxField("Universities", coerce=int)
    submit = SubmitField('Create FAQ')

class EditUniversityForm(Form):
    description = TextAreaField('University Description')
    submit = SubmitField('Update University')

class CreateUniversityForm(Form):
    name = TextField('University Name')
    description = TextAreaField('University Description')
    submit = SubmitField('Create University')

class EditMentorForm(Form):
    name = TextField('Name')
    email = TextField('Email')
    phone = TextField('Phone')
    university = SelectField('College of mentor', validators=[Required()], coerce=int)
    submit = SubmitField('Edit Mentor')

class EditProfileForm(Form):
    email = StringField('Email:', validators=[Email()])
    current_password = PasswordField('Current Password:')
    new_password = PasswordField('New Password:', validators=[Required(), EqualTo('new_password2', message='Passwords must match')])
    new_password2 = PasswordField('Re-enter Password:')
    submit = SubmitField('Save')
