from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.fields.core import IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from flask_app_basic.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(max=60), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    confirm_password = PasswordField('Confirm-Password', validators=[DataRequired(), Length(min=2, max=20), EqualTo('password')])

    submit = SubmitField('Sign up!')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user :
            raise ValidationError('That username is already taken! Please choose a different one.')
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('That email is already taken! Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    remember = BooleanField('Remember Me!')
    submit = SubmitField('Log in!')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(max=60), Email()])

    submit = SubmitField('Update!')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user :
                raise ValidationError('That username is already taken! Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()

            if email:
                raise ValidationError('That email is already taken! Please choose a different one.')

class SubmitMapRequestForm(FlaskForm):
    latitude = StringField('Latitude', validators=[DataRequired(), Length(min=2, max=60)])
    longitude = StringField('Longitude', validators=[DataRequired(), Length(min=2, max=60)])
    description = StringField('Short Description', validators=[Length(min=2, max=60)]) 
    picture = FileField('Add a picture!', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Submit Map Request! :)')


class CommitNotesForm(FlaskForm):
    commitNumber = IntegerField('commitNumber', validators=[Optional()])
    initialGraphics = StringField('initialGraphics', validators=[Optional(), Length(min=1, max=10000)])
    finalGraphics = StringField('finalGraphics', validators=[Optional(), Length(min=1, max=10000)])
    notes = StringField('notes', validators=[Optional(), Length(min=1, max=5000)])
    submit = SubmitField('Save all changes')

class CloneMapForm(FlaskForm):
    branch_name = StringField('Branch Name', validators=[DataRequired(), Length(min=1, max=20)])
    edit_access = StringField('Edit access', validators=[DataRequired(), Length(min=0, max=1000)])
    merge_access = StringField('Merge Access', validators=[DataRequired(), Length(min=0, max=1000)])
    submit = SubmitField('Confirm and Clone!')

class GetBranchForm(FlaskForm):
    branch_name = StringField('Branch Name', validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('Submit branch name')

class DeleteBranchForm(FlaskForm):
    submit = SubmitField('Delete this branch')

class MergeRequestForm(FlaskForm):
    merge_req_type = StringField('type', validators=[DataRequired()]) # request or accept
    from_branch = StringField('from', validators=[DataRequired(), Length(min=1, max=20)])
    to_branch = StringField('to', validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('submit')
