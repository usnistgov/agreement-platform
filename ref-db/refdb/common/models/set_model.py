import datetime
from ..core import db
import json
from bson import ObjectId
          
class SetModel(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    filename = db.StringField()
    raw_pressure = db.DictField() #{'aliq1':{'run1':[], 'run2':[]}, {'aliq2':{'run1':[], 'run2':[]}
    raw_uptake = db.DictField() #{'aliq1':{'run1':[], 'run2':[]}, {'aliq2':{'run1':[], 'run2':[]}
    fit_uptake = db.DictField() #{'aliq1':[], {'aliq2':[]}
    updated_from = db.StringField() #Another Set id. 
    possible_status = ["new", "used","empty","excluded","included","locked", "unlocked"]
    status = db.StringField(default="empty", choices=possible_status)

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def save(self, *args, **kwargs):
        self.created_at = str(datetime.datetime.utcnow())
        return super(SetModel, self).save(*args, **kwargs)

    def info(self):
        data = {'created-at':self.created_at, 'id':str(self.id),
        'filename':self.filename, 'raw-pressure':self.raw_pressure, 'raw-uptake':self.raw_uptake, 'fit-uptake':self.fit_uptake,
        'updated-from':self.updated_from, 'status':self.status}
        return data

    def summary(self):
        data = {'created-at':self.created_at, 'id':str(self.id),
        'filename':self.filename,
        'updated-from':self.updated_from, 'status':self.status}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))