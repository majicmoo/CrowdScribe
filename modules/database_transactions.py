from gluon import *
#db = current.db

#FIXME: Test all these manually to check they work and possibly construct unit tests.

def get_user(db, user_id):
    result = db(db.auth_user.id== user_id).select()
    return result

#TODO: Test this
def get_project(db, project_id):
    result = db(db.project.id == project_id).select()
    return result

def get_open_project(db, project_id):
    result = db(db.project.id == project_id).select()
    return result

#TODO: Test this
def get_document(db, document_id):
    result = db(db.document_image.id == document_id).select()
    return result


def get_all_projects(db):
    result = db().select(db.project.ALL)
    return result


def get_projects_by_user(db, user_id):
    result = db(db.project.author_id == user_id).select()
    return result


def get_open_projects_by_user(db, user_id):
    result = db((db.project.author_id == user_id)
                & (db.project.status == "Open")).select()
    return result


def get_closed_projects_by_user(db, user_id):
    result = db((db.project.author_id == user_id)
                & (db.project.status == "Closed")).select()
    return result


def get_project_documents(db, project_id):
    result = db(db.document_image.project_id == project_id).select()
    return result


def get_project_open_documents(db, project_id):
    result = db((db.document_image.project_id == project_id)
                & (db.document_image.status == "Open")).select()
    return result


def get_project_closed_documents(db, project_id):
    result = db((db.document_image.project_id == project_id)
                & (db.document_image.status == "Closed")).select()
    return result


def get_projects_by_tag(db, tag):
    # FIXME: Should this only be open projects?
    result = db(db.project.tag == tag).select()
    return result


def get_projects_by_keyword(db, keyword):
    result = db(((db.project.name.like('%' + keyword + '%')) | (db.project.description.like('%' + keyword + '%')))
                & (db.project.status == "Open")).select()
    return result


def get_transcriptions_by_user(db, user_id):
    result = db(db.transcription.author_id == user_id).select()
    return result


def get_transcribed_fields_for_transcription(db, transcription_id):
    result = db(db.transcribed_field.transcription_id == transcription_id).select()
    return result


def get_data_fields_for_project(db, project_id):
    result = db(db.data_field.project_id == project_id).select()
    return result


def get_transcriptions_for_document(db, document_id):
    # FIXME: I don;t think this returns transcriptions
    result = db((db.document_image.id == document_id) & (db.document_image.status == "Open")).select()
    return result


def get_done_documents_for_user(db, user_id):
    result = db((db.document_image.status == "Done")
                & (db.document_image.project_id == db.project.id)
                & (db.project.author_id == user_id) ).select()
    return result


def get_done_documents_for_project(db, project_id):
    result = db((db.document_image.status == "Done")
                & (db.document_image.project_id == project_id)).select()
    return result


def get_documents_for_a_user_that_have_transcription(db, user_id):
    result = db((db.document_image.project_id == db.project.id)
                & (db.project.author_id == user_id)
                & (db.document_image.id == db.transcription.document_id)
                & (db.transcription.status == "Open")).select()
    return result


def get_documents_for_a_project_that_have_transcription(db, project_id):
    result = db((db.document_image.project_id == project_id)
                & (db.document_image.id == db.transcription.document_id)
                & (db.transcription.status == "Open")).select()
    return result

def check_if_document_has_already_been_transcribed_by_user(db, document_id, user_id):
    result = db((db.document_image.id == db.transcription.document_id)
                &(db.document_image.id == document_id)
                &(db.transcription.author_id == user_id)).select()
    if result is None:
        return False
    else:
        return True


def get_documents_in_project_that_has_already_been_transcribed_by_user(db, project_id, user_id):
    result = db((db.project.id == db.document_image.project_id)
                &(db.document_image.id == db.transcription.document_id)
                &(db.project.id == project_id)
                &(db.transcription.author_id == user_id)).select()
    return result






