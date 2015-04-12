import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
from gluon import *

def all():

    allprojects = attach_header_image_to_projects(database.get_open_projects())

    return dict(allprojects = allprojects)

def attach_header_image_to_projects(projects):
    for project in projects:
        project.header_image = database.get_document_for_project_header(project.id).image

    return projects
