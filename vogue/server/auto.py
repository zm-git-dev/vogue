from werkzeug.contrib.fixers import ProxyFix

from vogue.server import create_app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)
