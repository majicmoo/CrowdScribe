import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
from gluon import *

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():

    #Page Title
    response.title = "CrowdScribe"

    # NOT REALLY LATEST PROJECTS
    latest_projects = database.get_open_projects()

    if len(latest_projects) == 0:
        latest_projects = []
        featured_project = None
        #print featured_project
        featured_project_image = None
    else:
        # Featured Project
        featured_project = latest_projects[0]
        featured_project_image = database.get_document_for_project_header(featured_project.id).image

    latest_projects = attach_header_image_to_projects(latest_projects)

    return dict(latest_projects = latest_projects, featured_project = featured_project,
                featured_project_image = featured_project_image)

def attach_header_image_to_projects(projects):
    for project in projects:
        project.header_image = database.get_document_for_project_header(project.id).image

    return projects

def browse():
    # Page Title
    response.title = "Browse"
    return dict(options = options)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
