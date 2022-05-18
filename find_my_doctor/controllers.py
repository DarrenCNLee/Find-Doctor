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
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, signed_url, Field
from .settings import APP_FOLDER
# import pandas as pd
import numpy as np
import os
import uuid
import random

url_signer = URLSigner(session)

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")
disease_file = os.path.join(APP_FOLDER, "data", "dataset.csv")

# The auth.user below forces login.


@action('index', method=["GET", "POST"])
@action.uses('index.html', url_signer, db, auth.user)
def index():

    symptom_list = (line.strip() for line in open(symptom_list_file))
    disease = np.genfromtxt(disease_file, delimiter=',', dtype=str)
    probability = np.zeros(disease.shape[0], dtype=float)

    rows = db(db.symptom.user_email == get_user_email()).select().as_list()
    rows_np = []

    for e in rows:
        rows_np.append(["symptom_list"])

    for i, e in enumerate(disease):
        counts = 17 - e[e == ''].shape[0]
        match = np.intersect1d(np.array(rows_np), e)
        probability[i] = match.shape[0]/counts

    form = Form(db.symptom, csrf_session=session, formstyle=FormStyleBulma)

    form.structure.find('[type=submit]')[0]['_value'] = 'Add'

    if form.accepted:
        redirect(URL('index'))

    return dict(rows=rows, form=form, symptoms=symptom_list, url_signer=url_signer, disease=disease, count=probability,
                search_url=URL('search', signer=url_signer))


@action('search')
@action.uses()
def search():
    q = request.params.get("q").lower()

    # scuffed way of getting symptom list (in lower case)
    rows = db(db.symptom.symptom_list).select().as_list()
    symptoms = list()
    for row in rows:
        symptoms.append(row['symptom_list'].lower())
    print("symptoms: " + str(symptoms))

    # check if the word starts with
    autocomplete = list()
    for symptom in symptoms:
        if(len(q.split(" ")) > 1):
            if symptom.startswith(q):
                autocomplete.append(symptom)
        else:
            for word in symptom.split(" "):
                if word.startswith(q):
                    autocomplete.append(symptom)
    print("autocomplete: " + str(autocomplete))
    results = results = db(
        (db.symptom.symptom_list == q) | (
            db.symptom.symptom_list == q.capitalize())
    ).select()

    for item in autocomplete:
        results |= db(
            (db.symptom.symptom_list == item) | (db.symptom.symptom_list == item.capitalize())).select()

    results = results.as_list()

    print(q, results)
    return dict(symptoms=symptoms, results=results)

# @action('add_symptom', method=["GET", "POST"])
# @action.uses('add_symptom.html', url_signer, db, session, auth.user)
# def add_symptom():
#     form = Form(db.symptom, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))

#     return dict(form=form)


@action("user_info")  # , method=["GET", "POST"]
@action.uses("user_info.html")  # , url_signer, db, session, auth.user
def user_info():
    # db get user_info of get_user_email return that
    #assert test
    # rows = db((db.user_info.user_email == get_user_email())).select()
    return dict(
        # rows=rows
    )

# @action("edit_user_info/<user_info_id:int>") #, method=["GET", "POST"]
# @action.uses("edit_user_info.html") #, url_signer, db, session, auth.user
# def user_info():
#     build form = Form
#               report = db(user_info)
#     form.accepted
#     redirect url user_info.htmll
#     return dict()


@action('edit_user_info/<user_info_id:int>', method=["GET", "POST"])
@action.uses('edit_user_info.html', url_signer.verify(), url_signer, db, session, auth.user)
def edit_user_info(user_info_id=None):
    assert user_info_id is not None
    user = db.user_info[user_info_id]

    if user["user_email"] != get_user_email() or user is None:
        redirect(URL('user_info'))

    form = Form(db.user_info, record=user, deletable=False, csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        redirect(URL('user_info'))

    return dict(form=form)


@action("edit")  # , method=["GET", "POST"]
@action.uses("edit.html")  # , url_signer, db, session, auth.user
def edit():
    return dict()


# @action("setup")
# @action.uses(db)
# def setup():
#     db(db.review).delete()


@action("get_rating")
@action.uses(db, auth.user)
def get_rating():
    doctor_id = request.params.get("doctor_id")
    rating = request.json.get("star_rating")
    assert doctor_id is not None and rating is not None
    db.stars.update_or_insert(
        ((db.review.doctor_id == doctor_id) & (db.review.rater == get_user())),
        doctor_id=doctor_id,
        rater=get_user(),
        star_rating=rating
    )
