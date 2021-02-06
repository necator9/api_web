from flask import request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.widgets import html5
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, ValidationError


button_types = {'START': 'Start app', 'STOP': 'Stop app', 'RESTART': 'Restart app', 'APP_STATUS': 'App status',
                'SWITCH_ON_LAMP': 'Lamp on'}


class UploadForm(FlaskForm):
    file = FileField('Upload {} file. Size < {} Kb'.format(current_app.config['UPLOAD_EXTENSIONS'],
                                                           current_app.config['MAX_CONTENT_LENGTH'] / 1024),
                     validators=[FileRequired()])
    submit = SubmitField('Upload and process')


class SetNodeParams(FlaskForm):
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    lamp_shutdown_interval = FloatField('Lamp shutdown interval, s', validators=[DataRequired()])
    dimm_lvl = FloatField('Dimming level', validators=[DataRequired()])
    bright_lvl = FloatField('Brightness level', validators=[DataRequired()])
    min_obj_speed = FloatField('Min obj. speed, m/s', validators=[DataRequired()])
    max_obj_speed = FloatField('Max obj. speed, m/s', validators=[DataRequired()])
    max_neighbour_distance = FloatField('Max neighbour_distance, m  ', validators=[DataRequired()])
    # light_distance = db.Column(db.Float)
    # toler_angles = db.Column(db.Float)

    submit = SubmitField('Submit')

    def compare(self, val, min_v, max_v):
        if not min_v <= val <= max_v:
            raise ValidationError('Set value in the range [{} - {}]'.format(min_v, max_v))

    def validate_latitude(self, latitude):
        self.compare(latitude.data, -85.05112878, 85.05112878)

    def validate_longitude(self, longitude):
        self.compare(longitude.data, -180, 180)

    def validate_lamp_shutdown_interval(self, lamp_shutdown_interval):
        self.compare(lamp_shutdown_interval.data, 0.1, 10000000000000)

    def validate_bright_lvl(self, bright_lvl):
        self.compare(bright_lvl.data, 0, 255)

    def validate_dimm_lvl(self, dimm_lvl):
        self.compare(dimm_lvl.data, 0, 255)

    def validate_min_obj_speed(self, min_obj_speed):
        self.compare(min_obj_speed.data, 0.5, 50)

    def validate_max_obj_speed(self, max_obj_speed):
        self.compare(max_obj_speed.data, 0.5, 50)

    def validate_max_neighbour_distance(self, max_neighbour_distance):
        self.compare(max_neighbour_distance.data, 3, 100)


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
