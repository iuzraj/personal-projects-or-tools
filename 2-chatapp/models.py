from flask import g
import config, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(3, 30)], render_kw={"placeholder":"Enter username..."})
    password = PasswordField("password", validators=[DataRequired(), Length(6, 80)], render_kw={"placeholder":"Enter password..."})
    repassword = PasswordField("repassword", validators=[DataRequired(), Length(6, 80)], render_kw={"placeholder":"ReEnter password..."})
    register = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(3, 30)], render_kw={"placeholder":"Enter username..."})
    password = PasswordField("password", validators=[DataRequired(), Length(6, 80)], render_kw={"placeholder":"Enter password..."})
    login = SubmitField("Login")


class GroupCreationForm(FlaskForm):
    groupname = StringField("groupname", validators=[DataRequired(), Length(3,60)], render_kw={"placeholder":"Group Name..."})
    read_only = BooleanField("read_only",)
    create = SubmitField("Create")


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
        user = self.query(f"SELECT * FROM users where {type} = ?", (id,))
        if not user: return None
        return User(user)
    
    def lookup_group(self, id, type="group_id"):
        group = self.query(f"SELECT * FROM groups where {type} = ?", (id,))
        if not group: return None
        return Group(group)
    
    def insert_user(self, username, password):
        password_hash = generate_password_hash(password)
        self.execute("INSERT INTO users (username, hashed_password, creation_dt) VALUES (?, ?, ?)", (username, password_hash, int(time.time())))
        
    def insert_group(self, groupname, creator_id, read_only):
        self.execute("INSERT INTO groups (groupname, creator_id, read_only, creation_dt) VALUES (?, ?, ?, ?)", (groupname, creator_id, read_only, int(time.time())))
        
    def insert_group_membership(self, member, group):
        self.execute("INSERT INTO group_memberships (group_id, member_id, last_seen) VALUES (?, ?, ?)", (group.group_id, member.user_id, int(time.time())))
        
    def fetch_invites(self, user):
        invites = self.query("SELECT * FROM group_invites WHERE user_id = ?", (user.user_id,), False)
        if not invites: return None
        return [Invite(invite) for invite in invites]
    
    def fetch_group_memberships(self, user):
        groups = self.query("SELECT * FROM group_memberships WHERE member_id = ?", (user.user_id,), False)
        if not groups: return None
        return [GroupMembership(group) for group in groups]
    
    def fetch_groups(self, user):
        memberships = self.fetch_group_memberships(user)
        groups = None
        if memberships:
            groups = [DB().lookup_group(membership.group_id) for membership in memberships]
        return groups
        
        
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
    
    def create_group(self, user, groupname, read_only):
        group = DB().lookup_group(groupname, "groupname")
        if group:
            return (False, "group name is taken.")
        DB().insert_group(groupname, user.user_id, read_only)
        DB().insert_group_membership(user, DB().lookup_group(groupname, "groupname"))
        return (True, "group created.")
        


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
    
    @property
    def invites(self):
        return DB().fetch_invites(self)
    
    @property
    def groups(self):
        return DB().fetch_groups(self)
    

class Invite:
    def __init__(self, data):
        self.invite_id = data["invite_id"]
        self.invite_to = data["invite_to"]
        self.invited_by = data["invited_by"]
        self.user_id = data["user_id"]
        self.invited_dt = data["invite_dt"]
    
    @property
    def inviter(self):
        return DB().lookup_user(self.invited_by)
    
    @property
    def groups(self):
        return DB().fetch_groups(self)
    
    
class Group:
    def __init__(self, data):
        self.group_id = data["group_id"]
        self.groupname = data["groupname"]
        self.creator_id = data["creator_id"]
        self.read_only = data["read_only"]
        self.creation_dt = data["creation_dt"]
        
        
class GroupMembership:
    def __init__(self, data):
        self.group_id = data["group_id"]
        self.member_id = data["member_id"]
        self.last_seen = data["last_seen"]