from flask import Blueprint, render_template, redirect, url_for, g, flash, request
from web_api_sl.forms import SetNodeParams, SearchForm, UpdateData, button_types
from web_api_sl.models import Node
from web_api_sl import db

bp = Blueprint('routes', __name__)


@bp.before_request
def before_request():
    g.search_form = SearchForm()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Index')


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate():
        return redirect(url_for('routes.index'))

    return redirect(url_for('routes.get', node_name=g.search_form.q.data))


def api_request(node_name):
    return False, {'name': node_name, 'app_status': True, 'latitude': 1022}


def send_api_request(key, value):
    import time
    time.sleep(5)
    return False


def process_api_request(new_node, old_node):
    new_node_d = new_node.object_as_dict()
    old_node_d = old_node.object_as_dict()
    submitted_fields = list()

    for key in new_node_d:
        if new_node_d[key] != old_node_d[key] and new_node_d[key] is not None:
            err = send_api_request(key, new_node_d[key])
            if err:
                flash('Error when submitting data')
            else:
                submitted_fields.append(key)
                setattr(old_node, key, getattr(new_node, key))
                db.session.add(old_node)
                db.session.commit()

    flash('Submitted keys: {}'.format(submitted_fields))


@bp.route('/get/<node_name>', methods=['GET', 'POST'])
def get(node_name):
    node = Node.query.filter_by(name=node_name).first()
    if not node:
        flash('No previous records for node {}'.format(node_name))

    update_form = UpdateData()
    if update_form.validate_on_submit():
        err, params = api_request(node_name)
        if err:
            flash('Error while fetching data')
            return render_template('show_params.html', node=node, update_form=update_form)

        if not node:
            node = Node(**params)
            db.session.add(node)
            db.session.commit()

        elif node:
            for key, value in params.items():
                setattr(node, key, value)
            db.session.add(node)
            db.session.commit()

    return render_template('show_params.html', node=node, update_form=update_form)


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
        process_api_request(new_node, node)

    if request.method == 'POST':
        print(request.form)
        for alias, button in button_types.items():
            if alias in request.form:
                flash(button)

    return render_template('set_params.html', node=node, node_form=node_form, buttons=button_types, node_name=node_name)
