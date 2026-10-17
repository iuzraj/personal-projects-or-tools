from flask import g
import config, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(3, 30)], render_kw={"placeholder":"Enter username..."})
    password = PasswordField("password", validators=[DataRequired(), Length(6, 80)], render_kw={"placeholder":"Enter password..."})
    repassword = PasswordField("repassword", validators=[DataRequired(), Length(6, 80)], render_kw={"placeholder":"ReEnter password..."})
    register = SubmitField("Register")


class DB:
    def __init__(self):
        self.con = g.con
        self.cur = g.con.cursor()
        
    def execute(self, query, params=()):
        self.cur.execute(query, params)
        self.con.commit()
        self.cur.close()
        
    def query(self, query, params=(), fetchone=True):
        self.cur.execute(query, params)
        if fetchone:
            data = self.cur.fetchone()
        else:
            data = self.cur.fetchall()
        self.cur.close()
        return data
    
    def lookup_user(self, id, type="user_id"):
        user = self.query(f"SELECT * FROM USERS where {type} = ?", (id,))
        if not user: return None
        return User(user)
    
    def insert_user(self, username, password):
        password_hash = generate_password_hash(password)
        self.execute("INSERT INTO users (username, hashed_password, creation_dt) VALUES (?, ?, ?)", (username, password_hash, int(time.time())))
        
        
class App:
    def register(self, username, password, confirm_password):
        if password != confirm_password:
            return (False, "passwords do not match.")
        user = DB().lookup_user(username, "username")
        if user is not None:
            return (False, "username taken.")
        DB().insert_user(username, password)
        return (True, "account created.")
    
    def login(self, username, password):
        user = DB().lookup_user(username, "username")
        if user is None:
            return (False, "user does not exist.")
        if not user.authenticate(password):
            return (False, "wrong password.")
        return (True, "logged in.", user.user_id)


class User:
    def __init__(self, data):
        self.user_id = data["user_id"]
        self.username = data["username"]
        self.namecolor = data["namecolor"]
        self.profile_picture = data["profile_picture"]
        if self.profile_picture == "default":
            self.profile_picture = config.DEFAULT_PROFILE_PICTURE
        self.hashed_password = data["hashed_password"]
        self.creation_dt = data["creation_dt"]
        
    def authenticate(self, password):
        return check_password_hash(self.hashed_password, password)