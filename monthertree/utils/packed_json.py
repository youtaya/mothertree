import json
from datetime import datetime, date

def get_date(create_date):
	return datetime.strptime(create_date, "%Y-%m-%d").date()

def toJSON(object):
	"""Dumps the data represented by the object to JSON for wire transfer."""
	return json.dumps(object, ensure_ascii=False)
