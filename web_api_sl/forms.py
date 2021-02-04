from flask import request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired


button_types = {'lamp_on': 'Lamp on', 'lamp_off': 'Lamp off', 'restart': 'Restart app'}


class UploadForm(FlaskForm):
    file = FileField('Upload {} file. Size < {} Kb'.format(current_app.config['UPLOAD_EXTENSIONS'],
                                                           current_app.config['MAX_CONTENT_LENGTH'] / 1024),
                     validators=[FileRequired()])
    submit = SubmitField('Upload and process')


class SetNodeParams(FlaskForm):
    latitude = FloatField('Latitude', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateData(FlaskForm):
    submit = SubmitField('Get relevant data')


class RemoveNode(FlaskForm):
    name = StringField('Hostname', validators=[DataRequired()])
    submit = SubmitField('Remove')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
