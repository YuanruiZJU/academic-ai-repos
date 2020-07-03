from db.models import model_from_name


class BaseObj(object):

    attrs = []
    model_name = ''

    def __init__(self):
        pass

    def from_dict(self, obj_dict):
        assert(isinstance(obj_dict, dict))
        for attr in self.attrs:
            try:
                val = obj_dict.get(attr)
            except KeyError:
                raise
            setattr(self, attr, val)

    def to_db_obj(self):
        try:
            db_cls = model_from_name(self.model_name)
            db_obj = db_cls()
            for attr in self.attrs:
                assert(hasattr(self, attr))
                val = getattr(self, attr)
                setattr(db_obj, attr, val)
            return db_obj
        except AttributeError:
            return None

    def from_db_obj(self, db_obj):
        for attr in self.attrs:
            try:
                attr_val = getattr(db_obj, attr)
            except AttributeError:
                raise
            setattr(self, attr, attr_val)

    def to_dict(self, required_attrs=None):
        ret_dict = dict()
        if required_attrs is None:
            required_attrs = self.attrs
        for a in required_attrs:
            ret_dict[a] = getattr(self, a)
        return ret_dict


