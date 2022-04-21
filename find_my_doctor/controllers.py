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

from this import d
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .settings import APP_FOLDER
# import pandas as pd
import numpy as np
import os

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")

@action("index")
@action.uses("index.html", auth, T)
def index():
    # user = auth.get_user()
    # message = T("Hello {first_name}".format(**user) if user else "Hello")
    # actions = {"allowed_actions": auth.param.allowed_actions}
    symptom_list = np.genfromtxt(symptom_list_file, dtype=str)
    return dict(symptoms=symptom_list)

@action("front_page")
@action.uses("front_page.html")
def front_page():
    symptom_list = np.genfromtxt(symptom_list_file, dtype=str)
    return dict(symptoms=symptom_list)

@action("user_info")
@action.uses("user_info.html")
def user_info():
    return dict()
