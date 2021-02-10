from flask import Blueprint, render_template, redirect, url_for, g, flash, request, current_app, abort
from web_api_sl.forms import SetNodeParams, SearchForm, UpdateData, button_types, UploadForm, RemoveNode
from web_api_sl.models import Node
from web_api_sl import db
from datetime import datetime
import os
from geojson import Point, Feature, LineString
from random import uniform

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
    return False, {'name': node_name, 'app_status': True, 'latitude': uniform(51.816096, 51.316096), 'longitude': 11.720393,
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


@bp.route('/all', methods=['GET', 'POST'])
def show_all():
    # app.config['POSTS_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    nodes = Node.query.order_by(Node.last_updated.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
    next_url = url_for('routes.show_all', page=nodes.next_num) if nodes.has_next else None
    prev_url = url_for('routes.show_all', page=nodes.prev_num) if nodes.has_prev else None
    return render_template("all.html", title='Show all', nodes=nodes.items, next_url=next_url, prev_url=prev_url)


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
    coordinates = [(node.longitude, node.latitude) for node in Node.query.all()]
    markers = [Feature(geometry=Point(pair)) for pair in coordinates]
    line = Feature(geometry=LineString(coordinates))

    return markers, line

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    coordinates = {'lat': 51.756845, 'long': 11.956438}
    token = current_app.config['MAPS_TOKEN']
    rows = db.session.query(Node).count()
    markers, line = gen_data_for_map()
    return render_template('index.html', title='Index', mapbox_access_token=token, coordinates=coordinates,
                           n_nodes=rows, markers=markers, line=line)


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
