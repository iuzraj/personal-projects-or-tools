from flask import Flask
import config
from routes import main_bp


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(main_bp)


if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE)