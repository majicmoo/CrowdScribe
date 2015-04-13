import os
# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

from gluon.custom_import import track_changes; track_changes(True)


options = ["Sport", "Theatre", "Military", "Journal Entries", "Architecture", "Citizen Information",
           "Religion", "Art", "Literature", "Finance", "Scientific", "Media", "Music", "Other"]

if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://crowdscribe.db', pool_size=1, check_reserved=['all'], lazy_tables=True)

    db.define_table('project',
                    Field('name'),
                    Field('author_id', 'reference auth_user', writable=False, readable=False),
                    Field('status'),
                    Field('description', type='text'),
                    Field('tag', requires=IS_IN_SET(options)),
                    Field('time_period_start_date', 'integer'),
                    Field('time_period_end_date', 'integer'),
                    Field('date_created', 'datetime'))

    db.define_table('document_image',
                    Field('description', type='text'),
                    Field('image', 'upload'),
                    Field('project_id', 'reference project'),
                    Field('status'))

    db.define_table('data_field',
                    Field('project_id', 'reference project'),
                    Field('name'),
                    Field('short_description', type='text'))

    db.define_table('transcription',
                    Field('document_id', 'reference document_image'),
                    Field('author_id', 'reference auth_user'),
                    Field('status'),
                    Field('date_created', 'datetime'))

    db.define_table('transcribed_field',
                    Field('data_field_id', 'reference data_field'),
                    Field('transcription_id', 'reference transcription'),
                    Field('information', type='text'))

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)


db.auth_user.first_name.readable = db.auth_user.first_name.writable = False
db.auth_user.last_name.readable = db.auth_user.last_name.writable = False
db.auth_user.email.readable = db.auth_user.email.writable = False
auth.settings.controller = 'user'

from gluon import current
current.db = db


## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

# Create a test database that's laid out just like the "real" database
import copy
test_db = DAL('sqlite://testing.db', pool_size=1, check_reserved=['all'], lazy_tables=True)  # Name and location of the test DB file
for tablename in db.tables:  # Copy tables!
    table_copy = [copy.copy(f) for f in db[tablename]]
    test_db.define_table(tablename, *table_copy)

current.test_db = test_db

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
db.project.description.widget = SQLFORM.widgets.text.widget
