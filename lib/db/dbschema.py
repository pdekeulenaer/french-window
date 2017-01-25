# schema.py

class Schema(object):
    def __init__(self, model_class):
        self.model = model_class
        self.table = None
        # self.view = None
        self.primary_key = None
        self.input_fields = []
        self.auto_fields = []

        self.foreign_keys = {}

    def is_valid(self):
        return (self.table is not None) and (self.model is not None)

    # Returns tuple (view, fields):
    #  view = the 'table' to view, this can be a join or a single table
    #  fields = the list of fields, including prefixes, to request
    def full_view(self):
        # create list
        assert self.is_valid()
        f = self.fields(True)
        q = self.table


        for (fk, o) in self.foreign_keys.items():
            # build join query
            q = '( %s LEFT OUTER JOIN %s ON %s.%s = %s.%s )' % (q, o.schema.table, self.table, fk, o.schema.table, o.schema.primary_key)
            # build field list
            f += o.schema.fields(True)

        return (q,f)

    # returns all the fields of this table, without prefix
    def fields(self, prefix=False):
        allfields = (self.input_fields + self.auto_fields + self.foreign_keys.keys())
        allfields.append(self.primary_key)
        unique_fields = list(set(allfields))
        # map prefix
        if prefix :
            unique_fields = map(lambda l: '%s.%s' % (self.table, l), unique_fields)
        return unique_fields

    def link_to_object(self, fk, to):
        self.foreign_keys[fk] = to

