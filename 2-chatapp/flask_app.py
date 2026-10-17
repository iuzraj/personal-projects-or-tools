from flask import Flask, g, request, session, redirect, url_for, flash
import config, sqlite3, models
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
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = models.DB().lookup_user(user_id)
        if user is None:
            session.pop("user_id")
    if request.endpoint not in ["main_bp.index", "main_bp.login", "main_bp.register"] and not user:
        flash("you need to log in to access that page.")
        return redirect(url_for("main_bp.index"))
    g.user = user


if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE)