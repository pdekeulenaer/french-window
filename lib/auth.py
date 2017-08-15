import web
import models
from db.dbschema import Schema

import hashlib

class User(models.Model):
    def __init__(self):
        self._is_authenticated = False
        super(User, self).__init__()

    @classmethod
    def set_schema(cls):
        schema = Schema(User)
        schema.table = 'users'
        schema.primary_key = 'id'
        schema.input_fields = ['name', 'password', 'email', 'level']
        schema.auto_fields = ['id']
        return schema

    def __str__(self):
        return self.name

    def is_authenticated(self):
        return self._is_authenticated

    def authenticate(self, provided_pw):
        if self.name is None or self.password is None:
            self._is_authenticated = False
            return self._is_authenticated

        hashpw = hashlib.sha256(provided_pw).hexdigest()

        if (self.password == hashpw):
            self._is_authenticated = True
        else:
            self._is_authenticated = False

        return self._is_authenticated

class Authenticator(object):
    def __init__(self, session):
        self.session = session

    # inputs: user = username, password = hashed password
    # Returns a user object if user logged in
    # Sets the user data in the session (TODO)
    def login(self, user, password):
        u = User.select({'name':user})
        if u is not None:
            u.authenticate(password)
        return u

    @classmethod
    def authenticated(cls, f):
        def wrapper(page, *args , **kwargs):
    	    if 'is_authenticated' in page.session.keys() and page.session.is_authenticated:
            	return f(page, *args, **kwargs)
    	    else:
                msg = 'Not logged in!'
    		return web.seeother('/auth/login/?msg='+msg)

        return wrapper

#define decorators
def authenticated(f):
    return Authenticator.authenticated(f)

User.schema = User.set_schema()


