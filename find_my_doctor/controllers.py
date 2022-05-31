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
import pandas as pd
import numpy as np
import os
import uuid
import random
import string

url_signer = URLSigner(session)

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")
disease_file = os.path.join(APP_FOLDER, "data", "dataset.csv")

# assigns a symptom to a user within the "has_symptom" db, inputs are an entry from the "user_info" and "symptoms" db


def has(u, s):
    db.has_symptom.update_or_insert(
        (
            (db.has_symptom.user_id == u.id) &
            (db.has_symptom.symptom_id == s.id)
        ),
        user_id=u.id,
        symptom_id=s.id,
    )

# The auth.user below forces login.


@action('index', method=["GET", "POST"])
@action.uses('index.html', url_signer, db, auth.user)
def index():

    # create symptoms db once
    symptom_list = np.genfromtxt(symptom_list_file, delimiter=',', dtype=str)
    if db(db.symptoms).isempty():
        for s in symptom_list:
            db.symptoms.insert(symptom_name=s)

    # create disease list, each line has the disease name first then followed by all the symptoms
    # disease_list = np.genfromtxt(disease_file, delimiter=',', dtype=str)
    disease_list = pd.read_csv(disease_file, sep=",", lineterminator="\n")
    # create empty probability for our regression model
    probability = pd.DataFrame(columns=["disease", "prob"])
    probability['disease'] = disease_list["Disease"]

    rows = db(db.symptom.user_email == get_user_email()).select().as_list()

    # initialize rows for model use
    user_symptoms = []
    prob_list = []
    for e in rows:
        user_symptoms.append(e['symptom_list'])
    user_symptoms = np.asarray(user_symptoms)
    # model calculation for corresponding symptoms to diseases
    for i, row in disease_list.iterrows():
        total = row.count()
        common = np.intersect1d(row.dropna().to_numpy(), user_symptoms)
        prob_list.append(common.shape[0] / total)

    probability['prob'] = prob_list
    probability = probability.sort_values(by=['prob'], ascending=False).drop_duplicates(
        subset=['disease'], keep='first').head(n=5)

    form = Form(db.symptom, csrf_session=session, formstyle=FormStyleBulma)
    form.structure.find('[type=submit]')[0]['_value'] = 'Add'

    if form.accepted:
        redirect(URL('index'))

    return dict(rows=rows, form=form, symptoms=symptom_list, url_signer=url_signer, disease=probability,
                search_url=URL('search', signer=url_signer))


@action('search')
@action.uses()
def search():
    q = request.params.get("q").lower()

    # scuffed way of getting symptom list (in lower case)
    rows = db(db.symptoms.symptom_name).select().as_list()
    symptoms = list()
    for row in rows:
        symptoms.append(row['symptom_name'].lower())
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
    results = db(
        (db.symptoms.symptom_name == q) | (
            db.symptoms.symptom_name == q.capitalize())
    ).select()

    for item in autocomplete:
        results |= db(
            (db.symptoms.symptom_name == item) | (db.symptoms.symptom_name == string.capwords(item))).select()

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
@action.uses("user_info.html", url_signer, db, session, auth.user)
def user_info(user_id=None):
    # db get user_info of get_user_email return that
    # assert test
    # rows = db(db.user_info.user_email == get_user_email()).select()
    # if rows is None:
    #     redirect(URL('add_user_info', user_id))
    user = db(db.user_info.user_email == get_user_email()).select().first()
    if user is None:
        redirect(URL("add_user_info"))
    assert user is not None
    return dict(
        # rows=rows,
        url_signer=url_signer,
        user=user,
    )


@action('add_user_info', method=["GET", "POST"])
@action.uses('add_user_info.html', url_signer, db, session, auth.user)
def add_user_info():
    form = Form([Field('First_Name', requires=IS_NOT_EMPTY(),),
                 Field('Last_Name', requires=IS_NOT_EMPTY()),
                 Field('Age', requires=IS_INT_IN_RANGE(0, 151)),
                 Field('Sex', requires=IS_IN_SET(["M", "F"]))],
                csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        db.user_info.insert(
            first_name=form.vars["First_Name"],
            last_name=form.vars['Last_Name'],
            age=form.vars['Age'],
            sex=form.vars['Sex'],)
        redirect(URL('user_info'))
    # form = Form(db.user_info, crsf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:
    #     redirect(URL('user_info'))
    return dict(form=form)


@action('edit_user_info/<user_info_id:int>', method=["GET", "POST"])
@action.uses('edit_user_info.html', url_signer.verify(), url_signer, db, session, auth.user)
def edit_user_info(
    user_info_id=None
):
    assert user_info_id is not None
    user = db.user_info[user_info_id]

    if user is None or user["user_email"] != get_user_email():
        redirect(URL('user_info'))

    form = Form(db.user_info, record=user, deletable=False, csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        redirect(URL('user_info'))

    return dict(form=form)


@action("get_rating")
@action.uses(db, auth.user)
def get_rating():
    doctor_id = request.params.get("doctor_id")
    rating = request.json.get("star_rating")
    assert doctor_id is not None and rating is not None
    db.stars.update_or_insert(
        ((db.review.doctor_id == doctor_id) &
         (db.review.rater == get_user_email())),
        doctor_id=doctor_id,
        rater=get_user_email(),
        star_rating=rating
    )
