from flask import request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.widgets import html5
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired


button_types = {'START': 'Start app', 'STOP': 'Stop app', 'RESTART': 'Restart app', 'APP_STATUS': 'App status',
                'SWITCH_ON_LAMP': 'Lamp on'}


class UploadForm(FlaskForm):
    file = FileField('Upload {} file. Size < {} Kb'.format(current_app.config['UPLOAD_EXTENSIONS'],
                                                           current_app.config['MAX_CONTENT_LENGTH'] / 1024),
                     validators=[FileRequired()])
    submit = SubmitField('Upload and process')


class SetNodeParams(FlaskForm):
    latitude = FloatField('Latitude', validators=[DataRequired()],
                          widget=html5.NumberInput(step=0.00000001, min=-85.05112878, max=85.05112878))
    longitude = FloatField('Longitude', validators=[DataRequired()],
                           widget=html5.NumberInput(step=0.00000001, min=-180, max=180))
    lamp_shutdown_interval = FloatField('Lamp shutdown interval', validators=[DataRequired()],
                                        widget=html5.NumberInput(step=0.1, min=0.1, max=10000000000000))
    bright_lvl = FloatField('Brightness level', validators=[DataRequired()],
                            widget=html5.NumberInput(step=1, min=0, max=255))
    dimm_lvl = FloatField('Dimming level', validators=[DataRequired()],
                          widget=html5.NumberInput(step=1, min=0, max=255))
    max_obj_speed = FloatField('Max obj. speed', validators=[DataRequired()],
                               widget=html5.NumberInput(step=0.5, min=0.5, max=50))
    min_obj_speed = FloatField('Min obj. speed', validators=[DataRequired()],
                               widget=html5.NumberInput(step=0.5, min=0.5, max=50))
    max_neighbour_distance = FloatField('Max neighbour_distance', validators=[DataRequired()],
                                        widget=html5.NumberInput(step=1, min=3, max=100))
    # light_distance = db.Column(db.Float)
    # toler_angles = db.Column(db.Float)
    submit = SubmitField('Submit')


class UpdateData(FlaskForm):
    submit = SubmitField('Update')


class RemoveNode(FlaskForm):
    name = StringField('Enter hostnames separated by comma', validators=[DataRequired()],
                       render_kw={'placeholder': '10.22.0.33, my_host_fqdn.com'})
    submit = SubmitField('Remove')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
