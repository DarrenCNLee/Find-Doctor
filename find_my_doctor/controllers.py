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
from .models import get_user_email, get_first_name, get_last_name
from pydal.validators import *
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, signed_url, Field
from .settings import APP_FOLDER
import pandas as pd
import numpy as np
import os
import requests
import uuid
import random
import string

api_key = "AIzaSyBgTJS9QCriBb51awuSN9QkDfo29LiTEqw"
url_signer = URLSigner(session)

symptom_list_file = os.path.join(APP_FOLDER, "data", "Symptom-list.csv")
disease_file = os.path.join(APP_FOLDER, "data", "dataset.csv")
specialist_dataset_file = os.path.join(
    APP_FOLDER, "data", "disease-doctor.csv")

symptom_list = np.genfromtxt(symptom_list_file, delimiter=',', dtype=str)
diseases = pd.read_csv(disease_file, sep=",", lineterminator="\n")
specialist_df = pd.read_csv(specialist_dataset_file, header=0, sep=",")

# print(diseases.columns)

specialist_list = specialist_df['specialist'].unique().tolist()


# specialist_list = ["Dermatologist", "Allergist", "Gastroenterologist", "General Physician", "Endocrinologist", "Pulmonologist", "Neurologist",    "Nephrologist", "Orthopedist", "Hepatologist", "Pulmonologist", "Otolaryngologist", "Cardiologist", "Phlebologist", "Rheumatologist", "Urologist"]

# doctor_names = ["Victoria Ahmad", "Andrea Alkyone", "Kamila Ryan", "Burhan Dejesus", "Georgia Puckett", "Keisha Bourne", "Caleb Grainger", "Piper Jeffery", "Amber Andersen", "Kanye Melia", "Otto Lee", "Finnlay Mcclure", "Astrid Krause", "Louie Freeman", "Gwen Cochran", "Emilie Rodrigues", "Elsa Morley", "Abu Murillo", "Stella Wainwright", "Ayyan Thatcher", "Aisling Hodge", "Maciej Mckay", "Ziva Wallace", "Oliwier Akhtar", "Jarred Mcneill", "David Mueller", "Reem Hall", "Ronnie Cruz", "Santino Hirst", "Nasir Reader", "Safwan Houston", "Abigayle Church", "Aeryn Hirst", "Campbell Espinosa", "Alana Hale", "Ian Shea", "Kiana Bateman", "Isabel Lyons", "Yasmin Thorpe", "Jakub Almond", "Antoni Lutz", "Jazmin Cresswell", "Kelsea English", "Faith Hoffman", "Robin Cain", "Momina Paterson", "Eduard Rich", "Ralphy Hinton", ]


# initialize disease model
class DiseaseModel():
    def __init__(self, symptom_list):
        self.symptom_list = symptom_list
        self.disease_list = []
        self.probability = []
        self.rows = db(db.symptom.user_email ==
                       get_user_email()).select().as_list()
        self.user_symptoms = []
        self.prob_list = []

        # create disease list, each line has the disease name first then followed by all the symptoms
        # disease_list = np.genfromtxt(disease_file, delimiter=',', dtype=str)
        self.disease_list = diseases
        # create empty probability for our regression model
        self.probability = pd.DataFrame(columns=["disease", "prob"])
        self.probability['disease'] = self.disease_list["Disease"]
        self.probability = pd.merge(
            self.probability, specialist_df, how="left")
        # print(self.probability)

    def predict(self):
        symptom_list = self.symptom_list
        if not self.user_symptoms:
            for e in self.rows:
                self.user_symptoms.append(e['symptom_name'])
            self.user_symptoms = np.asarray(self.user_symptoms)
        # model calculation for corresponding symptoms to diseases
        for i, row in self.disease_list.iterrows():
            total = row.count()
            common = np.intersect1d(
                row.dropna().to_numpy(), self.user_symptoms)
            self.prob_list.append(common.shape[0] / total)

        self.probability['prob'] = self.prob_list
        self.probability = self.probability.sort_values(by=['prob'], ascending=False).drop_duplicates(
            subset=['disease'], keep='first').head(n=5)

# The auth.user below forces login.


def check_sypmtom_exist(form):
    existing = db((db.symptom.symptom_name == form.vars['symptom_name']) & (
        db.symptom.user_email == get_user_email())).select().first()
    print(existing)
    if existing is not None:
        form.errors['symptom_name'] = T('Symptom already added')


@action('index', method=["GET", "POST"])
@action.uses('index.html', url_signer, db, auth.user)
def index():
    user = auth.get_user()
    if not user:
        redirect(URL('auth/login'))
    # create symptoms db once
    # symptom_list = np.genfromtxt(symptom_list_file, delimiter=',', dtype=str)
    # for s in symptom_list:
    #     db.symptoms.update_or_insert(symptom_name=s)

    # rows = db(db.symptom.user_email == get_user_email()).select().as_list()

    # initialize disease model and predict with the current symptom list
    disease_model = DiseaseModel(symptom_list)
    disease_model.predict()

    form = Form(db.symptom,
                validation=check_sypmtom_exist,
                csrf_session=session,
                formstyle=FormStyleBulma,
                form_name="Search symptoms",
                submit_value="Add")

    if form.accepted:
        redirect(URL('index'))

    # i=0
    # for specialist in specialist_list:
    #     for _ in range(3):
    #         db.doctor.update_or_insert(name=doctor_names[i],doctor_type=specialist)
    #         i+=1
    # del db.user_info[5]

    doc_list = db.doctor
    doc_list.truncate()

    person_info = db(db.user_info.user_email ==
                     get_user_email()).select().first()
    print(user)
    if person_info is None or person_info.location is None:
        need_location = True
        user_loc = "36.9741171%2C-122.0307963"
        # print("no location")
    else:
        need_location = False
        user_loc = person_info.lat + "%2C" + person_info.lng
        # print("location exists")

    return dict(form=form,
                need_location=need_location,
                api_key=api_key,
                user_loc=user_loc,
                symptoms=disease_model.symptom_list,
                url_signer=url_signer,
                disease=disease_model.probability,
                search_url=URL('search', signer=url_signer),
                load_symptoms_url=URL('load_symptoms', signer=url_signer),
                add_symptom_url=URL('add_symptom', signer=url_signer),
                delete_symptom_url=URL('delete_symptom', signer=url_signer),
                update_symptom_url=URL('update_symptom', signer=url_signer))


@action('load_symptoms')
@action.uses(url_signer.verify(), db, auth.user, url_signer)
def load_symptoms():
    rows = db(db.symptom.user_email == get_user_email()).select().as_list()
    # print(rows)
    return dict(symptom_list=rows)


@action('search')
@action.uses()
def search():
    q = request.params.get("q").lower()

    # scuffed way of getting symptom list (in lower case)
    rows = symptom_list.tolist()
    symptoms = list()
    for row in rows:
        symptoms.append(row.lower())
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
    results = []

    for s in rows:
        if s == q.capitalize() or s == q:
            results.append(s)

    for item in autocomplete:
        for s in rows:
            if (s == item) or (s == string.capwords(item)):
                if s not in results:
                    results.append(s)

    print(q, results)
    return dict(symptoms=symptoms, results=results)

# add a given symptom to a user's symptom list. put something in has_symptom table?


@action('delete_symptom', method='POST')
@action.uses(url_signer.verify(), db, auth.user, url_signer)
def delete_symptom():
    symptom = request.params.get('symptom')
    print(symptom)
    assert symptom is not None
    db((db.symptom.symptom_name == symptom) & (
        db.symptom.user_email == get_user_email())).delete()
    return "ok"


@action('update_symptom', method="POST")
@action.uses(url_signer.verify(), db)
def update_symptom():
    # get the from symptom_table
    symptom_name = request.json.get('symptom_name')

    print(symptom_name)
    db.symptom.update_or_insert(
        symptom_name=symptom_name,
        user_email=get_user_email(),
    )
    return "update symptom"


# @action('delete_symptom/<symptom_id:Str>')
# @action.uses(db, session, auth.user, url_signer.verify())
# def delete_symptom(symptom_id=None):
#     assert symptom_id is not None
#     db(db.symptom.symptom_list == symptom_id).delete()
#     redirect(URL('index'))

# for vue, not implemented yet, using link redirecting one above

# @action('delete_symptom')
# @action.uses(url_signer.verify(), db, auth.user, url_signer)
# def delete_symptom():
#     id = request.params.get('id')
#     assert id is not None
#     db(db.symptom.id == id).delete()
#     return "ok"

# @action('add_symptom', method=["GET", "POST"])
# @action.uses('add_symptom.html', url_signer, db, session, auth.user)
# def add_symptom():
#     form = Form(db.symptom, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))

#     return dict(form=form)

# @action('add_symptom', method="POST")
# @action.uses(url_signer.verify(), db, auth.user, url_signer)
# def add_symptom():
#     id = db.symptom.insert(
#         text=request.json.get('text'),          # author=request.json.get('author'),          # author=get_user_author(),      )
#     review_id = db.review.insert(
#         symptom_id=id
#     )

#     return dict(id=id, review_id=review_id, cur_author=cur_author)


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
    form = Form([Field('First_Name', requires=IS_NOT_EMPTY(), default=get_first_name),
                 Field('Last_Name', requires=IS_NOT_EMPTY(),
                       default=get_last_name),
                 Field('Location'),
                 Field('Age', requires=IS_INT_IN_RANGE(0, 151)),
                 Field('Sex', requires=IS_IN_SET(["Male", "Female", "Other"]))],
                csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        if form.vars['Location'] is "":
            loc = None
            lat = None
            lng = None
        else:
            loc = form.vars['Location']
            # https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=cruise&location=36.9741171%2C-122.0307963&radius=1500&key=AIzaSyBgTJS9QCriBb51awuSN9QkDfo29LiTEqw
            loc_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
                loc + "&key=" + api_key
            loc_info = requests.get(loc_url).json()
            loc_result = loc_info.get("results")[0]["geometry"]["location"]
            print(loc_result)
            lat = loc_result["lat"]
            lng = loc_result["lng"]

        db.user_info.insert(
            first_name=form.vars["First_Name"],
            last_name=form.vars['Last_Name'],
            location=loc,
            lat=lat,
            lng=lng,
            age=form.vars['Age'],
            sex=form.vars['Sex'],)
        redirect(URL('user_info'))
    # form = Form(db.user_info, crsf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:
    #     redirect(URL('user_info'))
    return dict(form=form)


@action('edit_user_info/<user_info_id:int>', method=["GET", "POST"])
@action.uses('edit_user_info.html', url_signer.verify(), url_signer, db, session, auth.user)
def edit_user_info(user_info_id=None):
    assert user_info_id is not None
    user = db.user_info[user_info_id]

    if user is None or user["user_email"] != get_user_email():
        redirect(URL('user_info'))

    # form = Form(db.user_info,
    #             record=user,
    #             deletable=False,
    #             csrf_session=session,
    #             formstyle=FormStyleBulma)

    # if form.accepted:
    #     redirect(URL('user_info'))

    # return dict(form=form)
    form = Form([Field('First_Name', requires=IS_NOT_EMPTY(), default=get_first_name),
                 Field('Last_Name', requires=IS_NOT_EMPTY(),
                       default=get_last_name),
                 Field('Location', default=user.location),
                 Field('Age', requires=IS_INT_IN_RANGE(
                     0, 151), default=user.age),
                 Field('Sex', requires=IS_IN_SET(["Male", "Female", "Other"]), default=user.sex)],
                csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        if form.vars['Location'] is "":
            loc = None
            lat = None
            lng = None
        else:
            loc = form.vars['Location']
            lat = user.lat
            lng = user.lng
            if loc != user.location:
                loc_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
                    loc + "&key=" + api_key
                loc_info = requests.get(loc_url).json()
                loc_result = loc_info.get("results")[0]["geometry"]["location"]
                print(loc_result)
                lat = loc_result["lat"]
                lng = loc_result["lng"]

        db.user_info[user_info_id] = dict(
            first_name=form.vars["First_Name"],
            last_name=form.vars['Last_Name'],
            location=loc,
            lat=lat,
            lng=lng,
            age=form.vars['Age'],
            sex=form.vars['Sex'],)

        redirect(URL('user_info'))

    return dict(form=form)


@action("doctors/<specialist>/<radius:int>", method=["GET", "POST"])
@action.uses('doctors.html', url_signer, db, session, auth.user)
def doctors(specialist=None, radius=None):
    assert specialist is not None

    doc_list = db.doctor
    doc_list.truncate()

    form = Form([Field('Radius', requires=[IS_IN_SET([5, 10, 20, 50]), IS_NOT_EMPTY()], default=radius)],
                csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        redirect(URL('doctors', specialist, form.vars['Radius']))

    person_info = db(db.user_info.user_email ==
                     get_user_email()).select().first()

    # print(user_loc, person_info.age)

    if specialist == "Previous":
        doctors_list = db(db.review.user_email ==
                          get_user_email()).select().as_list()
        print(doctors_list)
        if len(doctors_list) > 0:
            for doctor in doctors_list:
                db.doctor.insert(
                    name=doctor["doctor_name"],
                    address=doctor["doctor_type"])
        else:
            db.doctor.insert(
                name="No reviews yet",
                address="Review doctors to show their records here")

    else:
        assert person_info is not None or person_info.location is not None
        user_loc = person_info.lat + "%2C" + person_info.lng
        doctor_search = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=" + \
            specialist + "&location=" + user_loc + \
            "&types=doctor&radius=" + str(radius * 1500) + "&key=" + api_key
        doctors_list = requests.get(doctor_search).json()["results"]

        for doctor in doctors_list:
            db.doctor.insert(
                name=doctor["name"],
                address=doctor["vicinity"])

    return dict(form=form,
                specialist=specialist,
                load_reviews_url=URL('load_reviews', signer=url_signer),
                add_review_url=URL('add_review', signer=url_signer),
                delete_review_url=URL('delete_review', signer=url_signer),
                )


@action('load_reviews')
@action.uses(db, url_signer.verify())
def load_reviews():
    current_user_email = get_user_email()
    doctor_rows = db(db.doctor).select().as_list()
    review_rows = db(db.review).select().as_list()
    user_rows = db(db.user_info).select().as_list()
    r = db(db.user_info.user_email == get_user_email()).select().first()
    name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    return dict(doctor_rows=doctor_rows, review_rows=review_rows, user_rows=user_rows, name=name, current_user_email=current_user_email)


@action('add_review', method="POST")
@action.uses(db, url_signer.verify())
def add_review():
    r = db(db.user_info.user_email == get_user_email()).select().first()
    name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    doctor_reference = db(db.doctor.id == request.json.get(
        'doctor_id')).select().first()
    review_id = db.review.insert(
        doctor_name=request.json.get('doctor_name'),
        doctor_type=request.json.get('doctor_type'),
        star_rating=request.json.get('star_rating'),
        review_message=request.json.get('review_message'),
        name=name,
    )
    return dict(id=review_id, user_id=r.id, name=name)


@action('delete_review')
@action.uses(db, url_signer.verify(), session, auth.user)
def delete_review():
    id = request.params.get('id')
    assert id is not None
    db(db.review.id == id).delete()
    return "delete review"
