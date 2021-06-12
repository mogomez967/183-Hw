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
    'contact',
    Field('id'),
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email),
)

db.define_table(
    'phone',
    Field('contact_id', 'reference contact'),
    Field('phone_number', requires=IS_NOT_EMPTY()),
    Field('phone_name'),
)

db.contact.id.readable = False
db.contact.user_email.readable = db.contact.user_email.writable = False
db.phone.id.readable = False
db.commit()
