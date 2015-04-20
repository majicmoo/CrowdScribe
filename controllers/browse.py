import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)
from gluon import *

def all():
    # Controller for browse category
    response.title = "CrowdScribe | Browse"
    if request.args(0):
        all_projects = general_module.attach_all_information_to_projects(database.get_all_projects_for_category(request.args(0)))
        category_name = request.args(0)
    else:
        all_projects = general_module.attach_all_information_to_projects(database.get_open_projects())
        category_name = "All Projects"

    categories = current.tags
    return dict(allprojects = all_projects, categories = categories, category_name = category_name)


def category():
    # Controller for individual categories eg. art, sport
    # List of categories
    categories = current.tags
    categoryid = int(request.args(0))
    # Get current category
    category = categories[categoryid]
    response.title = "CrowdScribe | Browsing " + category
    # Get projects for current category
    projects = database.get_projects_for_tag(category)

    if not projects:
        # No projects currently available for this category
        session.flash = "No Projects currently available for " + category
        redirect(URL('browse', 'all'))
    projects = general_module.attach_all_information_to_projects(projects)
    return dict(category = category, projects = projects)
