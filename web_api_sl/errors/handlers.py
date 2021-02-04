from flask import render_template
from web_api_sl import db
from web_api_sl.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.errorhandler(413)
def too_large(e):
    return render_template('errors/413.html'), 413


@bp.errorhandler(400)
def wrong_format(e):
    return render_template('errors/400.html'), 400
