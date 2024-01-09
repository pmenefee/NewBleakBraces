import json
import datetime

class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(FirestoreEncoder, self).default(obj)