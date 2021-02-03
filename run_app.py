from web_api_sl import create_app, db
from web_api_sl.models import Node
from config import DevConfig

app = create_app(DevConfig)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Node': Node}
