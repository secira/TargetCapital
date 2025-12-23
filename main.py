from app import app
import routes_payment  # noqa: F401
import routes  # noqa: F401
import routes_broker  # noqa: F401
import routes_mobile  # noqa: F401

from routes_mobile_api import mobile_api
app.register_blueprint(mobile_api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
