"""
This file defines the database models
"""

from .common import db, Field
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

db.define_table(
    'user_info',
    Field('age', requires=IS_INT_IN_RANGE(0, 150)),
    Field('sex', requires=IS_IN_SET(["M", "F"])),
    Field('location', requires=IS_NOT_EMPTY()),
    Field('insurance_provider', requires=IS_NOT_EMPTY()),
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email),
)

db.user_info.id.readable = db.user_info.id.writable = False
# db.user_info.user_email.readable = db.user_info.user_email.writable = False

db.commit()