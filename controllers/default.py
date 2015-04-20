from gluon import *
import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import search_functions as search_functions
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)


def index():

    # Controller for the homepage of Crowdscribe
    # Max number of projects to be displayed on homepage per section
    number_of_projects_for_each_section = 6
    # Page Title
    response.title = "CrowdScribe | Home"
    # Latest projects that have been created
    latest_projects = database.get_latest_projects()
    # Projects with the most successfully transcribed documents
    most_transcribed_projects = database.get_most_transcribed_projects()
    if len(latest_projects) == 0:
        # If there are no latest projects
        latest_projects = []
        featured_project = None
        featured_project_image = None
    else:
        # Featured Project
        featured_project = latest_projects[0]
        featured_project_image = database.get_document_for_project_header(featured_project.id).image
        latest_projects = general_module.limit_list_of_projects(latest_projects, number_of_projects_for_each_section)

    most_transcribed_projects = general_module.limit_list_of_projects(most_transcribed_projects, number_of_projects_for_each_section)

    latest_projects = general_module.attach_all_information_to_projects(latest_projects)
    most_transcribed_projects = general_module.attach_all_information_to_projects(most_transcribed_projects)

    return dict(latest_projects = latest_projects, featured_project = featured_project,
                featured_project_image = featured_project_image, most_transcribed_projects=most_transcribed_projects)

def user():
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)


def call():
    return service()


@auth.requires_login()
def api():
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
