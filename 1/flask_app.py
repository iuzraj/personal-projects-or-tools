from flask import Flask
from flask import g, render_template, session, request, redirect, url_for, flash
import config, sqlite3, models
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
import bleach, allowed
from markupsafe import Markup 


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


def get_db_con():
    if "con" not in g:
        g.con = sqlite3.connect(config.DATABASE_FILE)
        g.con.row_factory = sqlite3.Row
    return g.con


@app.teardown_appcontext
def close_db_con(e):
    con = g.pop("con", None)
    if con is not None:
        con.close()


@app.before_request
def before_request():
    get_db_con()
    if request.endpoint not in ["login", "index", "entry"]:
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("login"))
        user = models.DB().get_user(user_id)
        if user is None:
            session.pop("user_id")
            return redirect(url_for("login"))
        g.user = user


@app.template_filter()
def sanitize(content):
    cleaned_content = bleach.clean(
        content,
        tags=allowed.ALLOWED_TAGS,
        attributes=allowed.ALLOWED_ATTRIBUTES,
        protocols=allowed.ALLOWED_PROTOCOLS,
        css_sanitizer=allowed.CSS_SANITIZER,
        strip=True,           
        strip_comments=True,
    )
    return Markup(cleaned_content)


class SearchForm(FlaskForm):
    entry_name = StringField("entry_name", validators=[DataRequired(), Length(1, config.MAX_ENTRY_NAME_SIZE)], render_kw={"placeholder":"Entry Name..."})
    entry_search = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def index():
    search_form = SearchForm()
    entries = None
    if search_form.validate_on_submit():
        entry_name = search_form.entry_name.data
        entries = models.DB().get_entries(entry_name)
        if not entries:
            flash("no entries found")
    return render_template("index.html", search_form=search_form, entries=entries)


class LoginForm(FlaskForm):
    login_username = StringField("login_username", validators=[DataRequired(), Length(config.MIN_USERNAME_SIZE, config.MAX_USERNAME_SIZE)], render_kw={"placeholder":"Username..."})
    login_password = PasswordField("login_password", validators=[DataRequired(), Length(config.MIN_PASSWORD_SIZE, config.MAX_PASSWORD_SIZE)], render_kw={"placeholder":"Password..."})
    login_submit = SubmitField("Login")


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_username = login_form.login_username.data
        login_password = login_form.login_password.data
        if not login_username.isalnum():
            flash("username can only contain alphabets and numbers")
        else:
            user = models.DB().get_user(login_username, "user_name")
            if not user:
                if login_username != config.SEED_USERNAME:
                    flash(f"user \"{login_username}\" does not exist")
                else:
                    models.DB().insert_user(login_username, login_password)
                    flash(f"user \"{login_username}\" added")
            else:
                if not user.authenticate(login_password):
                    flash("wrong password")
                else:
                    session["user_id"] = user.user_id
                    flash(f"logged in as \"{login_username}\"")
        return redirect(url_for("login"))
    return render_template("login.html", login_form=login_form)


class EntryForm(FlaskForm):
    entry_name = StringField("entry_name", validators=[DataRequired(), Length(config.MIN_ENTRY_NAME_SIZE, config.MAX_ENTRY_NAME_SIZE)], render_kw={"placeholder":"Entry Name..."})
    content = TextAreaField("content", validators=[DataRequired(), Length(config.MIN_CONTENT_SIZE, config.MAX_CONTENT_SIZE)], render_kw={"placeholder":"Entry Content..."})
    write = SubmitField("Add Entry")


@app.route("/write", methods=["GET", "POST"])
def write():
    user = g.user
    entry_form = EntryForm()
    if entry_form.validate_on_submit():
        entry_name = entry_form.entry_name.data
        if not entry_name.isalnum():
            flash("entry name can only have alphabets and numbers")
        else:
            entry = models.DB().get_entry(entry_name, "entry_name")
            if entry:
                flash("entry name is already taken")
            else:
                content = entry_form.content.data
                models.DB().insert_entry(user, entry_name, content)
                flash("entry added")
        return redirect(url_for("write"))
    return render_template("write.html", entry_form=entry_form, user=user)


@app.route("/entry")
def entry():
    entry_id = request.args.get("entry_id")
    if not entry_id:
        flash("no entry id provided")
        return redirect(url_for("index"))
    entry = models.DB().get_entry(entry_id)
    if not entry:
        flash("invalid entry id")
        return redirect(url_for("index"))
    return render_template("entry.html", entry=entry, user=entry.author)


class SettingsForm(FlaskForm):
    user_name = StringField("user_name", validators=[DataRequired(), Length(config.MIN_USERNAME_SIZE, config.MAX_USERNAME_SIZE)], render_kw={"placeholder":"Username..."})
    profile_picture = StringField("profile_picture", validators=[DataRequired(), Length(-1, 250)], render_kw={"placeholder":"Profile Picture Url..."})
    base_content = TextAreaField("base_content", validators=[Length(config.MIN_BASE_CONTENT_SIZE, config.MAX_BASE_CONTENT_SIZE)], render_kw={"placeholder":"Base Content..."})
    password = PasswordField("password", validators=[DataRequired(), Length(config.MIN_PASSWORD_SIZE, config.MAX_PASSWORD_SIZE)], render_kw={"placeholder":"Password..."})
    apply_changes = SubmitField("Apply Changes")


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("new_password", validators=[DataRequired(), Length(config.MIN_PASSWORD_SIZE, config.MAX_PASSWORD_SIZE)], render_kw={"placeholder":"New Password..."})
    new_password_confirm = PasswordField("new_password_confirm", validators=[DataRequired(), Length(config.MIN_PASSWORD_SIZE, config.MAX_PASSWORD_SIZE)], render_kw={"placeholder":"Confirm New Password..."})
    old_password = PasswordField("old_password", validators=[DataRequired(), Length(config.MIN_PASSWORD_SIZE, config.MAX_PASSWORD_SIZE)], render_kw={"placeholder":"Current Password..."})
    change_password = SubmitField("Change Password")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    user = g.user
    settings_form = SettingsForm()
    change_password_form = ChangePasswordForm()
    if request.method == "GET":
        settings_form.user_name.data = user.user_name
        settings_form.profile_picture.data = user.profile_picture
        settings_form.base_content.data = user.base_content
    if settings_form.validate_on_submit():
        new_username = settings_form.user_name.data
        if user.user_name != new_username and models.DB().get_user(new_username, "user_name"):
            flash(f"username \"{new_username}\" is taken")
        else:
            if not user.authenticate(settings_form.password.data):
                flash("wrong password")
            else:
                changes, values = ["user_name", "profile_picture", "base_content"], [new_username, settings_form.profile_picture.data, settings_form.base_content.data]
                for change in changes:
                    models.DB().execute(f"UPDATE users SET {change} = ? WHERE user_id = ?", (values[changes.index(change)], user.user_id))
                flash("changes applied")
        return redirect(url_for("settings"))
    if change_password_form.validate_on_submit():
        new_password = change_password_form.new_password.data
        confirm_new_password = change_password_form.new_password_confirm.data
        old_password = change_password_form.old_password.data
        if not user.authenticate(old_password):
            flash("wrong password")
        else:
            if new_password != confirm_new_password:
                flash("you typed the new password incorrectly")
            else:
                user.change_password(new_password)
                flash("password changed")
        return redirect(url_for("settings"))
    return render_template("settings.html", settings_form=settings_form, user=user, change_password_form=change_password_form)


if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE)