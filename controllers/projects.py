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


def add_transcription():

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

    form = FORM()

    #Display transcription submission form if document image is open for transcriptions and
    #user is authorised to make a submission
    if document.status != 'Done' and project.author_id != auth._get_user_id:
        for data_field in database.get_data_fields_for_project(db, project_id):
            label = '%s \n %s' % (data_field.name, data_field.short_description)
            text_input = INPUT(_name=data_field.name)
            form.append(SPAN(label, text_input))
            
        form.append(INPUT(_type='submit'))
            
        if form.process().accepts:
            transcription_id = db.transcription.insert(document_id=document_id, author_id=auth._get_user_id(), status='pending')
            for data_field in database.get_data_fields_for_project(db, project_id):
                print form.vars.data_field
                print form.vars
                db.transcribed_field.insert(data_field=data_field, transcription_id=transcription_id, information=form.vars.data_field)

    return dict(project=project, document=document, form=form)
