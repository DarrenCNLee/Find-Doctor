"""
This file defines the database models
"""

from .common import db, Field, auth, T
from pydal.validators import *
from .settings import APP_FOLDER
import os

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")
symptom_list = (line.strip() for line in open(symptom_list_file))

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
    Field('symptoms', requires=IS_NOT_EMPTY()),
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email),
)

db.define_table(
    'symptom',
    Field('symptom_list', requires=IS_IN_SET(symptom_list, zero=T('choose one'), error_message='must select from the list')),
    # Field('severity', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email),
)

db.define_table(
    'schedule',
    Field('working_days', requires=IS_IN_SET(["Mon", "Tue", "Wed", "Thur", "Fri"])),
    Field('booked_days', requires=IS_IN_SET(["Mon", "Tue", "Wed", "Thur", "Fri"])),
    Field('open_days', requires=IS_IN_SET(["Mon", "Tue", "Wed", "Thur", "Fri"])),
)

db.define_table(
    'doctor',
    Field('name', requires=IS_NOT_EMPTY()),
    Field('location', requires=IS_NOT_EMPTY()),
    Field('schedule_id', 'reference schedule'),
    Field('insurance_provider', requires=IS_NOT_EMPTY()),
    Field('doctor_type', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'review',
    Field('doctor_id', 'reference doctor'),
    Field('star_rating', requires=IS_FLOAT_IN_RANGE(0, 5)),
    Field('review_message'),
    Field('user_id', 'reference user_info'),
)


db.user_info.id.readable = db.user_info.id.writable = False
db.user_info.user_email.readable = db.user_info.user_email.writable = False
db.symptom.user_email.readable = db.symptom.user_email.writable = False

db.schedule.id.readable = db.schedule.id.writable = False
db.doctor.id.readable = db.doctor.id.writable = False
db.review.id.readable = db.review.id.writable = False

db.commit()
