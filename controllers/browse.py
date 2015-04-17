import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)
from gluon import *

def all():
    response.title = "CrowdScribe | Browse"

    categories = current.tags

    allprojects = general_module.attach_all_information_to_projects(database.get_open_projects())

    return dict(allprojects = allprojects, categories = categories)

def category():

    categories = current.tags
    categoryid = int(request.args(0))
    category = categories[categoryid]
    response.title = "CrowdScribe | Browsing "+category
    projects = database.get_projects_for_tag(category)

    if not(projects):
        session.flash = "No Projects currently available for "+category
        redirect(URL('browse', 'all'))

    projects = general_module.attach_all_information_to_projects(projects)

    return dict(category = category, projects = projects)
