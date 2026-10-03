from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
import time, config
from datetime import datetime


class DB:
    def __init__(self):
        self.con = g.con
        self.cur = self.con.cursor()
        
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
        return data
    
    def get_user(self, id, by="user_id"):
        query = f"SELECT * FROM users WHERE {by} = ?"
        params = (id,)
        data = self.query(query, params)
        if data is None:
            return None
        return User(data)
    
    def get_entry(self, id, by="entry_id"):
        query = f"SELECT * FROM entries WHERE {by} = ?"
        params = (id,)
        data = self.query(query, params)
        if data is None:
            return None
        return Entry(data)
    
    def get_entries(self, name):
        query = f"SELECT entry_id, entry_name, author_id, creation_dt FROM entries WHERE entry_name LIKE ? LIMIT 50"
        params = (f"%{name}%",)
        data = self.query(query, params, False)
        entries = []
        for entry in data:
            entries.append(Entry(entry))
        return entries
    
    def insert_user(self, user_name, password):
        password_hash = generate_password_hash(password)
        query = "INSERT INTO users(user_name, password_hash, creation_dt) VALUES (?, ?, ?)"
        params = (user_name, password_hash, int(time.time()))
        self.execute(query, params)
        
    def insert_entry(self, author, entry_name, content, password=None):
        query = "INSERT INTO entries (entry_name, content, author_id, creation_dt) VALUES (?, ?, ?, ?)"
        params = (entry_name, content, author.user_id, int(time.time()))
        if password:
            password_hash = generate_password_hash(password)
            query = "INSERT INTO entries (entry_name, content, author_id, creation_dt) VALUES (?, ?, ?, ?)"
            params = (entry_name, content, author.user_id, int(time.time()))
        self.execute(query, params) 
    
    
class User:
    def __init__(self, data):
        self.user_id = data["user_id"]
        self.user_name = data["user_name"]
        self.password_hash = data["password_hash"]
        self.profile_picture = data["profile_picture"]
        if self.profile_picture == "default":
            self.profile_picture = config.DEFAULT_PROFILE_PICTURE
        self.base_content = data["base_content"]
        self.creation_dt = data["creation_dt"]

    @property
    def dt(self):
        return datetime.fromtimestamp(self.creation_dt).strftime("%d-%m-%Y %H:%M:%S")

    def authenticate(self, password):
        return check_password_hash(self.password_hash, password)
    
    def change_password(self, new_password):
        password_hash = generate_password_hash(new_password)
        DB().execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, self.user_id))
        
        
class Entry:
    def __init__(self, data):
        self.data = data
        self.entry_id = data["entry_id"]
        self.entry_name = data["entry_name"]
        self.author_id = data["author_id"]
        self.creation_dt = data["creation_dt"]
        
    @property
    def author(self):
        return DB().get_user(self.author_id)
        
    @property
    def content(self):
        return self.data["content"]
    
    @property
    def dt(self):
        return datetime.fromtimestamp(self.creation_dt).strftime("%d-%m-%Y %H:%M:%S")