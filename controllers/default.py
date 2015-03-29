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
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    # NOT REALLY LATEST PROJECTS
    latest_projects = database.get_open_projects()

    # Featured Project
    featured_project = latest_projects[1]
    #print featured_project
    featured_project_image = database.get_document_image_for_project_header(featured_project.id).image

    return dict(latest_projects = latest_projects, database = database,
                featured_project = featured_project, featured_project_image = featured_project_image)

def browse():
    print "--------------Begin-------------"
    projects = database.get_open_projects()
    #Lists for SELECT() helper in advanced search form
    tags = ["All", "Sport", "Theatre", "Military", "Journal Entries", "Architecture", "Citizen Information",
           "Religion", "Art", "Literature", "Finance", "Scientific", "Media", "Music", "Other"]
    orders = ['Alphabetical', 'Earliest', 'Latest']
    #['Most accepted transcriptions', 'Fewest accepted transcriptions','Nearest completion', 'Farthest from completion']
    eras = ['BC','AD']

    #Creates advanced search form
    advanced = FORM(
        INPUT(_name='advance', _id="advancetext"),
        LABEL("Category", SELECT(tags, _name='tag', requires=IS_IN_SET(tags))),
        LABEL("Start Date", INPUT(_name='start_date', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,2016)))), #doesn't work atm
        SELECT(eras, _name='start_era', requires=IS_IN_SET(eras)),
        LABEL("End Date", INPUT(_name='end_date', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,2016)))), #doesn't work atm
        SELECT(eras, _name='end_era', requires=IS_IN_SET(eras)),
        LABEL("Include Unknown dates?", INPUT(_name='include_unknown_date', _type='checkbox')),
        LABEL("Sort by", SELECT(orders, _name='order', requires=IS_IN_SET(orders))),
        INPUT(_value='Refine search', _type='submit', _id="advancesubmit"),
        _action='', _method='GET'
    )
    
    #Determine how to order results. If none specified (ie, new search), default
    #order alphabetically
    if request.vars.order == 'Earliest':
        projects = database.get_open_projects().sort(lambda project: project.time_period_start_date)
    elif request.vars.order == 'Latest':
        projects = database.get_open_projects().sort(lambda project: project.time_period_end_date, reverse=True)
    else:
        projects = database.get_open_projects().sort(lambda project: project.name)
    
    print request.vars
    
    #Gets keywords
    if request.vars.search is not None:
        searchstr = request.vars.quicksearch
        advanced.vars.advance = request.vars.quicksearch
    elif request.vars.advance is not None:
        searchstr = request.vars.advance
        advanced.vars.advance = request.vars.advance
    else:
        searchstr = None

    print searchstr
    #Filters by keywords (in name and description)
    if searchstr is not None:
        projects.exclude(lambda project: (searchstr.upper() not in project.name.upper())
            and (searchstr.upper() not in project.description.upper()))

    #Filters by tag
    if (request.vars.category != 'All') and (request.vars.category is not None):
        projects.exclude(lambda project: str(request.vars.tag) != str(project.tag))

    #Filters by date
    if (request.vars.start_date is not None or request.vars.start_date == "") and (request.vars.start_date is None or request.vars.start_date != ""):
        start_date = convert_date_to_integer(request.vars.start_date, request.vars.start_era)
        advanced.vars.start_date = request.vars.start_date
        advanced.vars.start_era = request.vars.start_era
    else:
        start_date = -2016

    if (request.vars.end_date is not None or request.vars.end_date == "") and (request.vars.end_date is None or request.vars.end_date != ""):
        end_date = convert_date_to_integer(request.vars.end_date, request.vars.end_era)
        advanced.vars.end_date = request.vars.end_date
        advanced.vars.end_era = request.vars.end_era
    else:
        end_date = 2016

    if request.vars.start_date is not None or request.vars.end_date is not None:
        #Excludes unknown dates
        if request.vars.include_unknown_date != "on":
            #exclude if end before start date or start after end date
            projects.exclude(lambda project: (project.time_period_start_date is None) or
                (project.time_period_end_date < start_date) or (end_date < project.time_period_start_date))

        #Includes unknown dates
        else:
            #exclude if before start date or after end date or Date is none
            projects.exclude(lambda project: (project.time_period_end_date < start_date) or
                (end_date < project.time_period_start_date))
            
    #Have to clear request.vars before processing otherwise consecutive
    #searches accumulate into lists rather than individual elements
    #advanced.vars = request.vars
    request.vars = {}

    if advanced.process(onvalidation=date_validator).accepted:
        #advanced.vars=request.vars
        redirect(URL('browse', vars=advanced.vars))
    elif advanced.errors:
        response.flash='errors'

    return dict(advanced=advanced, projects=projects, database=database)

def convert_date_to_integer(date, era):
    if era =="BC":
        return -int(date)
    else:
        return int(date)
    
def date_validator(advanced):
    #Check that start date is before end date
    if ((request.vars.start_date is not None or request.vars.start_date == "") and (request.vars.start_date is None or request.vars.start_date != "") and
        (request.vars.end_date is not None or request.vars.end_date == "") and (request.vars.end_date is None or request.vars.end_date != "")):
        
        start = convert_date_to_integer(request.vars.start_date,request.vars.start_era)
        end = convert_date_to_integer(request.vars.end_date,request.vars.end_era)
        if start > end:
            advanced.errors.time_period_end_date = 'The End Date of the time period must be later than the Start Date'
            


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
