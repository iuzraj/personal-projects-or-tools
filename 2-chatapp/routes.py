from flask import Blueprint, render_template, flash, redirect, url_for
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