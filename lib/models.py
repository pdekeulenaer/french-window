# A class to define the basic functionality each 'object' in the model will have
# Last updated: 7/1/2016
# Author: Philip De Keulenaer

from db import get_db
import util

class Model(object):
    def __init__(self):
        self.__setattr__(self.schema.primary_key, None)

    @classmethod
    def set_schema(cls):
        schema = Schema(cls)
        return schema

    def schema(cls):
        return cls.schema

    # returns the primary key
    def pk(self):
        pk = eval('self.%s' % (self.schema.primary_key))
        return pk

    # Returns if this primary key is valid or not - an invalid PK means the object is not yet saved
    def valid_pk(self):
        pk = self.pk()
        if pk is None: return False
        if str(pk).lstrip('-').isdigit() and int(pk) < 0: return False
        if pk == '': return False
        return True


    def update(self, valuemap):
        for el in self.schema.input_fields:
            if el in valuemap.keys():
                self.__setattr__(el, valuemap[el])

    def save(self):
        if (not self.valid_pk()):
            uid = self._store()
            self.__setattr__(self.schema.primary_key, uid)
            return uid
        else:
            return self._db_update()

    def _db_update(self):
        valuemap = {}
        for el in list(self.schema.input_fields):
            valuemap[el] = (eval('self.%s' % el))
        get_db().update(self.schema, self.pk(), valuemap)
        return self.id

    def _store(self):
        valuemap = {}
        for el in list(self.schema.input_fields):
            valuemap[el] = eval('self.%s' % el)

        entryid = get_db().store(self.schema, valuemap)
        return entryid

    # assumes a unique ID
    def delete(self):
        # delete based on ID
        assert self.id > 0
        get_db().delete(self.schema, [('id','=',self.id)])

    def link_models(self):
        pass

    # Fix prefix of parameters
    @classmethod
    def fix_prefix(cls, params):
        table = cls.schema.table
        # if a fieldname has a prefix, ignore; otherwise add main prefix
        nparams = {}
        for (k,v) in params.items():
            if ('.' in k):
                nparams[k] = v
            else:
                nparams['%s.%s' % (table, k)] = v

        return nparams

    #  assumes fully qualified fields
    @classmethod
    def prune_fields(cls, params):
        params = cls.fix_prefix(params) # Force fully qualified fields
        p = {}
        (_, valid_fields) = cls.schema.full_view()
        for (k,v) in params.items():
            if k in valid_fields:
                p[k] = v

        return p


    # searches one record specified with 'AND' parameters
    # params is a map with field -> value pairs
    @classmethod
    def select(cls, params, sort={}):
        p = cls.fix_prefix(params)
        sort = cls.fix_prefix(sort)
        res = get_db().select(cls.schema, p,sort)

        if res is None:
            return None
        return cls.from_dict(res)

    # returns a list of all matching objects (in order returned by query)
    # assuming exact matches (e.g., lookups by keys, ids, etc)
    @classmethod
    def select_all(cls, params={}, sort={}):
        p = cls.fix_prefix(params)
        sort = cls.fix_prefix(sort)
        res = get_db().select_all(cls.schema, p, sort)
        if res is None: return
        objects = []

        # convert lists to objects
        for obj in res:
            objects.append(cls.from_dict(obj))

        return objects

    @classmethod
    def search(cls, exact={}, approx={}, sort={}):
        ex = cls.fix_prefix(exact)
        appr = cls.fix_prefix(approx)
        sort = cls.fix_prefix(sort)
        res = get_db().search(cls.schema, ex, appr, sort)
        if res is None: return []
        objects = []

        # convert lists to objects
        for obj in res:
            objects.append(cls.from_dict(obj))

        return objects

    # convert a set of fields and corresponding values an book object
    @classmethod
    def from_tuple(cls, fields, values):
        d = dict(zip(fields,values))
        return cls.from_dict(d)

    @classmethod
    def from_dict_only(cls, d):
        obj = cls()
        # set this class' objects
        class_fields = cls.schema.fields(prefix=True)

        for (k,v) in d.items():
            if (k in class_fields):
                obj.__setattr__(k.split('.')[1],v)

        return obj

    # convert a set of fields and corresponding values into a book object
    @classmethod
    def from_dict(cls, d):
        d = cls.fix_prefix(d)
        if d is None:
            return None

        obj = cls.from_dict_only(d)
        # for each foreign key, set their fields
        for (fk, f_class) in (cls.schema.foreign_keys.items()):
                fk_objname = f_class.__name__.lower()
                f_obj = f_class.from_dict_only(d)
                obj.__setattr__(fk_objname, f_obj)

        obj.link_models()
        return obj

    @classmethod
    def delete_id(cls, obj_id):
        get_db().delete(cls.schema, [('id','=',obj_id)])


    @classmethod
    def search_plus(cls, params):
        obj = cls.select(params)
        if (obj is None) or (params is None):
            obj = cls.from_dict(params)
            uid = obj.save()
        return obj



    def json_parse(self, maxdepth=1, level=0):
        resp = {}
        for (k,v) in self.__dict__.items():
            if not callable(k):
                # print '%s: serializing %s' % (str(self), str(k))
                if isinstance(v,Model):
                    if level >= maxdepth:
                        resp[k] = None
                    else :
                        resp[k] = v.json_parse(maxdepth=maxdepth, level=level+1)
                elif isinstance(v, list):
                    resp[k] = map(lambda l: l.json_parse(maxdepth=maxdepth, level=level),v)
                else:
                    resp[k] = v
        return resp
