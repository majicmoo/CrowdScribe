import database_transactions as database

def create():
    return dict()


def project():

    project_id = request.args(0)
    project = database.get_open_project(db, project_id)

    #If project doesnt exist or isn't open, redirect
    if project is None:
        redirect(URL('default','index'))

    #If user owns project then initialise message to be displayed on page
    if project.author_id == auth._get_user_id():
        response.flash = DIV("You own this project", _class="alert alert-info")

    documents_for_project = database.get_project_open_documents(db, project.id)
    data_fields_for_project = database.get_data_fields_for_project(db, project.id)

    #Retrieve documents that have already been transcribed by the user in this project. This
    #can be used to alert users to that fact on the page.
    documents_transcribed_by_user = database.get_documents_in_project_that_has_already_been_transcribed_by_user\
                                    (db, project_id, auth._get_user_id())


    return dict(project=project, documents_for_project=documents_for_project,
                data_fields_for_project=data_fields_for_project,
                documents_transcribed_by_user = documents_transcribed_by_user)


def add_transctiption():

    #Remove if project data not required in page
    project_id = request.args(0)
    project = database.get_open_project(db, project_id)

    if project is None:
        redirect(URL('default','index'))

    document_id = request.args(1)
    document = database.get_document(db, document_id)

    if document is None:
        redirect(URL('projects','project',args=[project_id]))

    if project.author_id == auth._get_user_id():
        response.flash = DIV("You own this project", _class="alert alert-info")

    if auth._get_user_id is None:
        response.flash = DIV("Please register to transcribe", _class="alert alert-info")

    form is None:

    #Display transcription submission form if document image is open for transcriptions and
    #user is authorised to make a submission
    if document.status != 'Done' and project.author_id != auth._get_user_id:
        form = SQLFORM(db.transcription_field, showid=False, formstyle='divs')

    return dict(project=project, document=document, form=form)
