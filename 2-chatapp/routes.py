from flask import Blueprint, render_template, flash, redirect, url_for, session, g, request
import models


main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    register_form = models.RegistrationForm()
    if register_form.validate_on_submit():
        username = register_form.username.data
        password = register_form.password.data
        repassword = register_form.repassword.data
        status = models.App().register(username, password, repassword)
        flash(status[1])
        return redirect(url_for("main_bp.register"))
    return render_template("register.html", form=register_form)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    form = models.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        status = models.App().login(username, password)
        flash(status[1])
        if status[0] is True:
            session["user_id"] = status[2]
            return redirect(url_for("main_bp.home"))
        return redirect(url_for("main_bp.login"))
    return render_template("login.html", form=form)


@main_bp.route("/home", methods=["GET", "POST"])
def home():
    group_form = models.GroupCreationForm()
    if group_form.validate_on_submit():
        groupname = group_form.groupname.data
        read_only = group_form.read_only.data
        status = models.App().create_group(g.user, groupname, int(read_only))
        flash(status[1])
        if status[0] is True:
            return redirect(url_for("main_bp.home"))
        return redirect(url_for("main_bp.home"))
    return render_template("home.html", user=g.user, group_form=group_form)


@main_bp.route("/group", methods=["GET", "POST"])
def group():
    group_id = request.args.get("group_id")
    group = models.DB().lookup_group(group_id)
    if not group:
        flash("invalid group id.")
        group_id = None
    if not group_id:
        return redirect(url_for("main_bp.home"))
    return render_template("group.html", user=g.user, group=group)