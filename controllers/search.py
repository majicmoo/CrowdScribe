import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
from gluon import *

def search_results():

    # Page Title
    response.title = "Search Results"    

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
        LABEL("Start Date", INPUT(_name='start_date', _class='integer', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,2016)))), #doesn't work atm
        SELECT(eras, _name='start_era', requires=IS_IN_SET(eras)),
        LABEL("End Date", INPUT(_name='end_date', _class='integer', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,2016)))), #doesn't work atm
        SELECT(eras, _name='end_era', requires=IS_IN_SET(eras)),
        LABEL("Include Unknown dates?", INPUT(_name='include_unknown_date', _type='checkbox')),
        LABEL("Sort by", SELECT(orders, _name='order', requires=IS_IN_SET(orders))),
        INPUT(_value='Refine search', _type='submit', _id="advancesubmit"), _method='GET'
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
    if request.vars.quicksearch is not None:
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

    #Does not validate
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
