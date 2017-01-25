from auth import authenticated

class NewPage(object):

    session = None
    model = None

    def __init__(self):
        self.setUp()

    def setUp(self):
        self.session = session
        self.model = model
        self.module_name = type(model).__name__
        self.render = web.template.render('site/'+self.module_name)
        self.auth = lib.auth.Authenticator(self.session)


    def msg(self):
        data = web.input()
        if 'msg' in data.keys():
            return data['msg']
        return ''

    @classmethod
    def urls(cls):
        clsname = cls.__name__
        return ('/%s/(.+)/(.*)' % (cls.model.__name__), clsname, '/%s/' % (cls.model.__name__), clsname)

    def GET(self, page=None, *args, **kwargs):
        if page is None: return self.list()
        elif page == 'list' : return self.list()

    # get methods
    @authenticated
    def list(self):
        data = web.input()
        data['user_id'] = self.session.user_id
        objs = self.module.select_all(self.module.prune_fields(data))
        return render.list(message=self.msg(), objects=objs)


