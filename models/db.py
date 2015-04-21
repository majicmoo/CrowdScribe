import os

from gluon.custom_import import track_changes; track_changes(True)


options = ["Sport", "Theatre", "Military", "Journal Entries", "Architecture", "Citizen Information",
           "Religion", "Art", "Literature", "Finance", "Scientific", "Media", "Music", "Other"]

if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://crowdscribe.db', pool_size=1, check_reserved=['all'], lazy_tables=True)

    db.define_table('project',
                    Field('name', length=55),
                    Field('author_id', 'reference auth_user', writable=False, readable=False),
                    Field('status'),
                    Field('description', type='text', length=500),
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
                    Field('name', length=55),
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
    db = DAL('google:datastore+ndb')
    session.connect(request, response, db=db)

response.generic_patterns = ['*'] if request.is_local else []

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
current.tags = options


## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.messages.logged_in = 'You are now Logged In'
auth.messages.logged_out = 'You are now Logged Out'
