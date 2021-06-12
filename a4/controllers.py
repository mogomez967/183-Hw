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
import itertools

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, SPAN
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

from py4web.utils.dbstore import DBStore
from py4web.utils.form import Form, FormStyleBulma
from .common import Field

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():

    header_list = ['First Name', 'Last Name', ' ', 'Phone Numbers']
    # connect the 'phone' db to 'contact' db
    db(db.phone.contact_id == db.contact.id).select()

    # store names in rows
    rows = db(db.contact.user_email == get_user_email()).select()

    # temp list to store dict that holds phone #s (s) and descriptions (l)
    # s = []
    # l = []

    # for i in db(db.phone.contact_id == db.contact.id).select(db.phone.phone_number, db.phone.phone_name).as_list():
    #     s.append(i)

    # for j in db(db.phone).select(db.phone.phone_name).as_list():
    #     l.append(j)

    # numbers = []
    # names = []

    # to grab the phone_names and place into a list
    # for i in range(0, len(l)):
    #     for j in l[i].values():
    #         names.append(j)

    # create a string in which I append each char of the number
    # then take that string and append it to numbers[] with the addition of (phone_name)
    # for itor, item in enumerate(s):
    #     tut = ""
    #     for index in item["phone_number"]:
    #         tut += str(index)
    #     numbers.append(tut + str(" (" + str(names[itor]) + ")"))

    # for itor in s:
    #     temp = ""
    #     friend = ""
    #     for index, undex in itertools.zip_longest(itor["phone_number"], itor["phone_name"], fillvalue=""):
    #         friend += index
    #         temp += undex
    #     numbers.append(friend + " " + "(" + temp + ")")
    #
    # print("numbers[]: ", numbers)

    salt = db(db.phone.contact_id == db.contact.id).select(db.phone.contact_id, db.phone.phone_number, db.phone.phone_name)
    # print("salt: ", salt)
    # print("rows[]: ", rows, type(rows), type(salt))

    return dict(
        headers=header_list,
        rows=rows,
        salt=salt,
        url_signer=url_signer,
    )

@action('add_contact', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_contact.html')
def add():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_contact.html')
def edit(contact_id=None):
    assert contact_id is not None
    b = db.contact[contact_id]
    if b is None:
        redirect(URL('index'))
    form = Form(db.contact, record=b, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(
        form=form
    )

@action('display_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'display_phone.html')
def edit(contact_id=None):
    assert contact_id is not None

    headers = ['Phone', 'Name']
    s = []
    for i in db(db.phone).select(db.phone.phone_number, db.phone.phone_name).as_list():
        s.append(i)

    rows = db(db.phone.contact_id == contact_id).select()

    # print("rows in display_phone: ", rows)
    return dict(
        headers=headers,
        rows=rows,
        contact_id=contact_id,
        url_signer=url_signer,
    )

@action('edit_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, url_signer.verify(), 'edit_phone.html')
def edit(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None

    form = Form([Field('phone_number'), Field('phone_name')], csrf_session=session,
                formstyle=FormStyleBulma)
    if form.accepted:
        row = db(db.phone.contact_id == contact_id).select().first()
        row.update_record(phone_number=form.vars["phone_number"], phone_name=form.vars["phone_name"])
        redirect(URL('index'))

    return dict(form=form)

@action('add_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, session, url_signer.verify(), 'add_phone.html')
def add_phone(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None

    form = Form([Field('phone_number'), Field('phone_name')], csrf_session=session,
                formstyle=FormStyleBulma)
    if form.accepted:
        db.phone.insert(
            contact_id=contact_id,
            phone_number=form.vars["phone_number"],
            phone_name=form.vars["phone_name"]
        )
        redirect(URL('index'))
    return dict(form=form)

@action('delete/<contact_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete(contact_id=None):
    assert contact_id is not None
    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

@action('delete_phone/<contact_id:int>/<phone_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_phone(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    db(db.phone.id == phone_id).delete()
    redirect(URL('index'))
