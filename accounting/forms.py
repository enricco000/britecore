from wtforms import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class PolicyForm(Form):
    policy_item = StringField('Policy number',
                              validators=[DataRequired(), Length(min=2, max=128)])
    submit = SubmitField('Query')


class AgentForm(Form):
    agent = StringField('Name of the Agent',
                        validators=[DataRequired(), Length(min=1, max=128)])
    submit = SubmitField('Query')
