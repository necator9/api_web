from flask import Blueprint, render_template, redirect, url_for, g, flash, request, current_app, abort
from web_api_sl.forms import SetNodeParams, SearchForm, UpdateData, button_types, UploadForm, RemoveNode
from web_api_sl.models import Node
from web_api_sl import db
from datetime import datetime
import os
from geojson import Point, Feature, LineString

bp = Blueprint('routes', __name__)


@bp.before_request
def before_request():
    g.search_form = SearchForm()


def send_api_request(key, value):
    import time
    time.sleep(2)
    return False


def get_api_request(node_name):
    send_api_request(None, None)
    return False, {'name': node_name, 'app_status': True, 'latitude': 51.816096, 'longitude': 11.720393,
                   'lamp_shutdown_interval': 2, 'bright_lvl': 40, 'dimm_lvl': 3, 'max_obj_speed': 20,
                   'min_obj_speed': 2, 'max_neighbour_distance': 50}


def process_get_api_request(node, node_name):
    err, params = get_api_request(node_name)

    if err:
        return err

    if not node:
        node = Node(**params)
        db.session.add(node)
        db.session.commit()

    elif node:
        for key, value in params.items():
            setattr(node, key, value)
        db.session.add(node)
        db.session.commit()


def process_set_api_request(new_node, old_node):
    new_node_d = new_node.object_as_dict()
    old_node_d = old_node.object_as_dict()
    submitted_fields = list()
    db_modified = False

    for key in new_node_d:
        if new_node_d[key] != old_node_d[key] and new_node_d[key] is not None:
            err = send_api_request(key, new_node_d[key])
            if err:
                flash('Error when submitting data')
            else:
                submitted_fields.append(key)
                setattr(old_node, key, getattr(new_node, key))
                db_modified = True

    if db_modified:
        old_node.timestamp = datetime.utcnow()
        db.session.add(old_node)
        db.session.commit()

    flash('Submitted keys: {}'.format(submitted_fields))


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(uploaded_file.filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            data = uploaded_file.read().decode('ascii').splitlines()
            for node_name in data:
                node = Node.query.filter_by(name=node_name).first()
                err = process_get_api_request(node, node_name)
                if err:
                    flash('Error while fetching data from {}'.format(node_name))

    return render_template('upload.html', title='Upload', form=upload_form)


@bp.route('/remove', methods=['GET', 'POST'])
def remove():
    remove_form = RemoveNode()
    if remove_form.validate_on_submit():
        hosts_to_remove = remove_form.name.data.replace(' ', '').split(',')
        for hostname in hosts_to_remove:
            node = Node.query.filter_by(name=hostname).first()
            if node:
                Node.query.filter_by(name=hostname).delete()
                # node.delete()
                db.session.commit()
                flash('Node {} deleted'.format(hostname))
            else:
                flash('No such node: {}'.format(hostname))
        redirect(url_for('routes.remove'))

    return render_template('remove.html', title='Remove', form=remove_form)


def gen_data_for_map():
    coordinates = [[-77.0366048812866, 38.89873175227713],
                   [-77.03364372253417, 38.89876515143842],
                   [-77.03364372253417, 38.89549195896866],
                   [-77.02982425689697, 38.89549195896866],
                    [-77.02400922775269, 38.89387200688839],
                    [-77.01519012451172, 38.891416957534204],
                    [-77.01521158218382, 38.892068305429156],
                    [-77.00813055038452, 38.892051604275686],
                    [-77.00832366943358, 38.89143365883688],
                    [-77.00818419456482, 38.89082405874451],
                    [-77.00815200805664, 38.88989712255097]]

    markers = [Feature(geometry=Point(pair)) for pair in coordinates]
    line = Feature(geometry=LineString(coordinates))

    return markers, line
# ROUTE = [
#     {"lat": 64.0027441, "long": -22.7066262, "name": "Keflavik Airport", "is_stop_location": True},
#     {"lat": 64.0317168, "long": -22.1092311, "name": "Hafnarfjordur", "is_stop_location": True},
#     {"lat": 63.99879, "long": -21.18802, "name": "Hveragerdi", "is_stop_location": True},
#     {"lat": 63.4194089, "long": -19.0184548, "name": "Vik", "is_stop_location": True}]

coords_arr = [{"lat": 64.0027441, "long": -22.7066262},
              {"lat": 64.0317168, "long": -22.1092311}]
def create_stop_locations_details():
    stop_locations = []
    for location in ROUTE:
        # Skip anything that is not a stop location
        if not location["is_stop_location"]:
            continue
        # Create a geojson object for stop location
        point = Point([location['long'], location['lat']])
        properties = {
            'title': location['name'],
            'icon': 'campsite',
            'marker-color': '#3bb2d0',
            'marker-symbol': len(stop_locations) + 1
        }
        feature = Feature(geometry=point, properties = properties)
        stop_locations.append(feature)
    return stop_locations

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    coordinates = {'lat': 51.756845, 'long': 11.956438}
    token = current_app.config['MAPS_TOKEN']
    rows = db.session.query(Node).count()
    markers, line = gen_data_for_map()
    return render_template('index.html', title='Index', mapbox_access_token=token, coordinates=coordinates,
                           n_nodes=rows, coords=coords_arr, markers=markers, line=line, test=None)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate():
        return redirect(url_for('routes.index'))

    return redirect(url_for('routes.get', node_name=g.search_form.q.data))


@bp.route('/get/<node_name>', methods=['GET', 'POST'])
def get(node_name):
    node = Node.query.filter_by(name=node_name).first()
    if not node:
        flash('No previous records for node {}'.format(node_name))

    update_form = UpdateData()
    if update_form.validate_on_submit():
        err = process_get_api_request(node, node_name)
        if err:
            flash('Error while fetching data from {}'.format(node_name))
            return render_template('show_params.html', node=node, update_form=update_form)
        return redirect(url_for('routes.get', node_name=node_name))

    return render_template('show_params.html', node=node, update_form=update_form, title='Get')


@bp.route('/set/<node_name>', methods=['GET', 'POST'])
def set(node_name):
    node = Node.query.filter_by(name=node_name).first()
    if not node:
        flash('No previous records for node {}'.format(node_name))
        return redirect(url_for('routes.get', node_name=node_name))

    node_form = SetNodeParams(obj=node)

    if node_form.validate_on_submit():
        new_node = Node()
        node_form.populate_obj(new_node)
        process_set_api_request(new_node, node)

    if request.method == 'POST':
        for alias, button in button_types.items():
            if alias in request.form:
                flash(button)

    return render_template('set_params.html', node=node, node_form=node_form, buttons=button_types,
                           node_name=node_name, title='Set')
