import database_transactions as database

def create():
    return dict()


def project():

    project_id = request.args(0)
    project = database.get_open_project(project_id).first()

    #If project doesnt exist or isn't open, redirect
    if project is None:
        redirect(URL('default','index'))

    #If user owns project then initialise message to be displayed on page
    if project.author_id == auth._get_user_id():
        response.flash = DIV("You own this project", _class="alert alert-info")

    documents_for_project = database.get_project_open_documents(project.id)
    data_fields_for_project = database.get_data_fields_for_project(project.id)

    #Retrieve documents that have already been transcribed by the user in this project. This
    #can be used to alert users to that fact on the page.
    documents_transcribed_by_user = database.get_documents_in_project_that_has_already_been_transcribed_by_user\
                                    (project_id, auth._get_user_id())


    return dict(project=project, documents_for_project=documents_for_project,
                data_fields_for_project=data_fields_for_project,
                documents_transcribed_by_user = documents_transcribed_by_user)
