from auth import authenticated, Authenticator
import web
import json
import re

class Controller(object):

    session = None
    model = None

    def __init__(self):
        self.setUp()

    def setUp(self):
        self.module_name = self.model.__name__.lower()
        renderlink =  'site/'+self.module_name+'/'
        self.render = web.template.render(renderlink, base='../base', globals={'session':self.session})
        self.auth = Authenticator(self.session)
        self.functions =  {
            'list' : 'list',
            'view' : 'view',
            'add' : 'add' }

    def register(self, func, view=None):
        if view is None:
            view = func
        self.functions[func] = view

    def msg(self):
        data = web.input()
        if 'msg' in data.keys():
            return data['msg']
        return ''

    @classmethod
    def urls(cls):
        clsname = cls.__name__
        return ('/%s/(.+)/' % (cls.model.__name__.lower()), clsname, '/%s/' % (cls.model.__name__.lower()), clsname)

    def GET(self, page=None, *args, **kwargs):
        return self._process('GET',page, *args, **kwargs)

    def POST(self, page=None, *args, **kwargs):
        return self._process('POST',page, *args, **kwargs)

    def _process(self, method, page=None, *args, **kwargs):
        # get the function name to execute
        fname = self.functions.setdefault(page, None)

        # first test if the method exists in specific mode
        f_specific = fname + '_' + method.lower()
        f = getattr(self, str(f_specific), None)
        if callable(f):
            return f(*args, **kwargs)

        # get the generic function
        f = getattr(self, str(fname), None)
        if callable(f):
            return f(*args, **kwargs)

        # if we reach this, no function was found
        return Error.invalid_url()

    def clearfunctions(self):
        self.functions = {}

    @authenticated
    def list_data(self):
        data = web.input()
        data['user_id'] = self.session.user_id
        objs = self.model.select_all(self.model.prune_fields(data))
        return objs

    @authenticated
    def list(self, *args):
        objs = self.list_data()
        return self.render.list(message=self.msg(), objects=objs)

    @authenticated
    def ajax_list(self,*args):
        objs = self.list_data()
        obj_dicts = map(lambda l: l.json_parse(), objs)
        return json.dumps(obj_dicts)

    @authenticated
    def view_data(self,o_id=None):
        if o_id is None or not(o_id.isdigit()): Error.invalid_id()

        # return the object data
        o = self.model.select({self.model.schema.primary_key : int(o_id)})
        if o is None: Error.object_not_found()
        if 'user_id' in o.schema.fields():
            if o.user_id != self.session.user_id: Error.invalid_user()
        return o

    def view(self, o_id=None):
        o = self.view_data(o_id)
        return self.render.view(message=self.msg(), object=o)

    @authenticated
    def add(self):
        data = web.input()
        data['user_id'] = self.session.user_id
        obj = self.model.from_dict(data)
        uid = obj.save()
        return self.render.add(message=self.msg())

    @authenticated
    def ajax_add(self):
        data = web.input()
        data['user_id'] = self.session.user_id
        data['summary'] = sanitize(data.summary)
        obj = self.model.from_dict(data)
        uid = obj.save()
        return json.dumps('OK')

    @authenticated
    def ajax_delete(self):
        data = web.input()

        obj = self.model.select({'id':data.id})

        if obj is None: return Error.invalid_id()
        if obj.user_id != self.session.user_id: return Error.invalid_user()

        obj.delete()

        return json.dumps('OK')

# error messages
class Error(object):
    @staticmethod
    def invalid_id(msg='No valid identifier specified', redirect='/'):
        Error.redirect(msg, redirect)

    @staticmethod
    def object_not_found(msg='Object not found', redirect='/'):
        Error.redirect(msg, redirect)

    @staticmethod
    def invalid_user(msg='Not yours to view', redirect='/'):
        Error.redirect(msg, redirect)

    @staticmethod
    def invalid_url(msg='This page does not exist', redirect='/'):
        Error.redirect(msg, redirect)

    @staticmethod
    def redirect(msg, redirect):
        web.seeother(redirect + '?msg=' + msg)


