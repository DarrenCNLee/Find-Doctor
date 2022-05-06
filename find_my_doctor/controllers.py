"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from pydal.validators import *
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .settings import APP_FOLDER
# import pandas as pd
import numpy as np
import os

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")


@action("index")
@action.uses("index.html", auth, T) #, url_signer, db, auth.user
def index():

    symptom_list = (line.strip() for line in open(symptom_list_file))
    # symptom_list = np.genfromtxt(symptom_list_file, dtype=str)
    form = Form([Field('symptomps', requires=IS_IN_SET(symptom_list, zero=T('choose one'), error_message='must select from the list'))],
                deletable=False,
                csrf_session=session,
                formstyle=FormStyleBulma)

    return dict(form=form, symptoms=symptom_list)


# @action("front_page")
# @action.uses("front_page.html")
# def front_page():
#     symptom_list = np.genfromtxt(symptom_list_file, dtype=str)
#     return dict(symptoms=symptom_list)


@action("user_info") #, method=["GET", "POST"]
@action.uses("user_info.html") #, url_signer, db, session, auth.user
def user_info():
    #db get user_info of get_user_email return that
    #assert test
    return dict()

# @action("edit_user_info/<user_info_id:int>") #, method=["GET", "POST"]
# @action.uses("edit_user_info.html") #, url_signer, db, session, auth.user
# def user_info():
#     build form = Form
#               report = db(user_info)
#     form.accepted
#     redirect url user_info.htmll
#     return dict()

@action("edit")  #, method=["GET", "POST"]
@action.uses("edit.html")#, url_signer, db, session, auth.user
def edit():
    return dict()
