from flask import Flask, g, request, session, redirect, url_for
import config, sqlite3
from routes import main_bp


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(main_bp)


def get_db_con():
    db = getattr(g, "con", None)
    if db is None:
        g.con = sqlite3.connect(config.DATABASE_FILE)
        g.con.row_factory = sqlite3.Row


@app.teardown_appcontext
def close_connection(e):
    db = g.pop("con", None)
    if db is not None:
        db.close()
        
        
@app.before_request
def before_request():
    get_db_con()


if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE)