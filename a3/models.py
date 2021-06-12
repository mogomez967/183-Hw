"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'bird',
    ### TODO: define the fields that are in the json.
    # my additions to the table
    Field('id'),
    Field('bird', requires=IS_NOT_EMPTY()),
    Field('weight', 'integer'),
    Field('diet'),
    Field('habitat'),

    # n_sightings and user_email fields
    Field('bird_count', 'integer'),
    Field('seen_by', default=get_user_email),   # removed '()'
)

db.bird.id.readable = False
db.bird.seen_by.readable = db.bird.seen_by.writable = False
db.commit()
