from flask import Blueprint, render_template, redirect, url_for, g, flash, request
from web_api_sl.forms import NodeParams, SearchForm, UpdateData
from web_api_sl.models import Node

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

    req_hostname = g.search_form.q.data
    node = Node.query.filter_by(name=req_hostname).first()
    params_form = NodeParams()
    get_form = UpdateData()
    if get_form.validate_on_submit():
        flash('Updating')
        params_form.name.data = node.name
        params_form.app_status.data = node.app_status
        params_form.latitude.data = node.latitude

    if params_form.validate_on_submit():
        flash('Data submitted')
        # return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET' and node:
        params_form.name.data = node.name
        params_form.app_status.data = node.app_status
        params_form.latitude.data = node.latitude
    elif not node:
        flash('No previous records for node {}'.format(req_hostname))

    return render_template('node_stats.html', hostname=req_hostname, node=node, form=params_form, get_form=get_form)

