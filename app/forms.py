from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, HiddenField, validators
from wtforms.validators import DataRequired

# class LoginForm(Form):
#     openid = StringField('openid', validators=[DataRequired()])
#     remember_me = BooleanField('remember_me', default=False)

class IndexForm(FlaskForm):
    member_id = StringField('member_id', validators=[DataRequired()])
    # member_id = StringField('member_id')
    # member_id = StringField('memberid', validators=[DataRequired()])
    # remember_me = BooleanField('remember_me', default=False)

    # Complex validation
    # http://flask.pocoo.org/snippets/64/

    # def __init__(self, *args, **kwargs):
    #     Form.__init__(self, *args, **kwargs)
    #
    #     self.user = None
    #
    # def validate(self):
    #     rv = Form.validate(self)
    #     if not rv:
    #         return False
    #
    #     user = User.query.filter_by(
    #         username=self.username.data).first()
    #
    #     if user is None:
    #         self.username.errors.append('Unknown username')
    #         return False
    #
    #     if not user.check_password(self.password.data):
    #         self.password.errors.append('Invalid password')
    #         return False
    #
    #     self.user = user
    #     return True


class StorageForm(FlaskForm):
    slot_id = StringField('slot', validators=[DataRequired()])
    member_name = StringField('name', validators=[DataRequired()])
    member_email = StringField('email', validators=[DataRequired()])
    member_phone = StringField('phone', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    completion = StringField('completion', validators=[DataRequired()])


class RegisterToVoteForm(FlaskForm):
    hidden = HiddenField()

    register = SubmitField(label='Send My Registration Email')
    cancel = SubmitField(label='Cancel Voting Request')


class MemberNotFoundForm(FlaskForm):
    hidden = HiddenField()


class ServerErrorForm(FlaskForm):
    hidden = HiddenField()
