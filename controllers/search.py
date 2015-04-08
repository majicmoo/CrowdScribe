import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
from gluon import *

def search_results():

    # Page Title
    response.title = "Search Results"    
    
    # Lists for SELECT() helper in advanced search form
    tags = ["All", "Sport", "Theatre", "Military", "Journal Entries", "Architecture", "Citizen Information",
           "Religion", "Art", "Literature", "Finance", "Scientific", "Media", "Music", "Other"]
    eras = ['BC','AD']
    orders = ['Alphabetical', 'Earliest', 'Latest']
    #['Most accepted transcriptions', 'Fewest accepted transcriptions','Nearest completion', 'Farthest from completion']

    # Creates advanced search form
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
    
    # Start with all open projects in the database as results
    projects = database.get_open_projects()

    ###Filter by keyword###
    # Gets keywords
    if request.vars.quicksearch is not None:
        searchstr = request.vars.quicksearch
        advanced.vars.advance = request.vars.quicksearch
    elif request.vars.advance is not None:
        searchstr = request.vars.advance
        advanced.vars.advance = request.vars.advance
    else:
        searchstr = None

    # Filter excludes results which do not include any keywords in either project title or description
    if searchstr is not None:
        keywords = searchstr.split(' ')
        projects.exclude(lambda project: search_project_for_keywords(keywords, project))

    ###Filter by category###
    if (request.vars.category != 'All') and (request.vars.category is not None):
        projects.exclude(lambda project: str(request.vars.tag) != str(project.tag))

    ###Filter by date###
    if not empty_date_field(request.vars.start_date):
        start_date = convert_date_to_integer(request.vars.start_date, request.vars.start_era)
        advanced.vars.start_date = request.vars.start_date
        advanced.vars.start_era = request.vars.start_era
    else:
        # Ensures all dates pass (if validation is fixed)
        start_date = -2016

    if not empty_date_field(request.vars.end_date):
        end_date = convert_date_to_integer(request.vars.end_date, request.vars.end_era)
        advanced.vars.end_date = request.vars.end_date
        advanced.vars.end_era = request.vars.end_era
    else:
        # Ensures all dates pass (if validation is fixed)
        end_date = 2016

    if not empty_date_field(request.vars.start_date) or not empty_date_field(request.vars.end_date):
        # Excludes unknown dates
        if request.vars.include_unknown_date != "on":
            # Exclude if end_date is before project's start date, start_date after project's end date or if project dates are none
            projects.exclude(lambda project: (project.time_period_start_date is None) or
                (project.time_period_end_date < start_date) or (end_date < project.time_period_start_date))

        # Includes unknown dates
        else:
            # Exclude if end_date is before project's start date or start_date after project's end date
            projects.exclude(lambda project: (project.time_period_end_date < start_date) or
                (end_date < project.time_period_start_date))
            
    ###Order results###
    if request.vars.order == 'Earliest':
        # Order by earliest start date
        projects = projects.sort(lambda project: project.time_period_start_date)
    elif request.vars.order == 'Latest':
        # Order by latest end date
        projects = projects.sort(lambda project: project.time_period_end_date, reverse=True)
    else:
        # Order alphabetically (default)
        projects = projects.sort(lambda project: project.name)

    """
    Have to clear request.vars before processing otherwise consecutive
    searches accumulate into lists rather than individual elements
    advanced.vars = request.vars
    """
    request.vars = {}
    
    #Does not validate
    if advanced.process(onvalidation=date_validator).accepted:
        #advanced.vars=request.vars
        redirect(URL('search', vars=advanced.vars))
    elif advanced.errors:
        response.flash='errors'

    projects = attach_header_image_to_projects(projects)

    return dict(advanced=advanced, projects=projects)


def attach_header_image_to_projects(projects):
    for project in projects:
        project.header_image = database.get_document_for_project_header(project.id).image

    return projects


def search_project_for_keywords(keywords, project):
    exclude = True
    
    # Search project for keywords. If word is found, project is not excluded
    for word in keywords:
        if (word.upper() in project.name.upper()) or (word.upper() in project.description.upper()):
            exclude = False
            break
        
    return exclude


def convert_date_to_integer(date, era):
    if era =="BC":
        return -int(date)
    else:
        return int(date)
    
def empty_date_field(date):
    if (date is not None or date == "") and (date is None or date != ""):
        #Date field has content
        return False
    else:
        return True

def date_validator(advanced):
    #Checks start date is after 2015 BC
    if not empty_date_field(advanced.vars.start_date):
        if convert_date_to_integer(advanced.vars.start_date) < -2015:
            advanced.errors.start_date = 'Start date must be after 2015 BC'
            
    #Checks end date is before 2015 AD
    if not empty_date_field(advanced.vars.end_date):
        if convert_date_to_integer(advanced.vars.end_date) > 2015:
            advanced.errors.end_date = 'End date must be before 2015 AD'        
            
    #Check that start date is before end date if there are entries for both dates
    if not empty_date_field(advanced.vars.start_date) and not empty_date_field(advanced.vars.end_date):
        start = convert_date_to_integer(advanced.vars.start_date, advanced.vars.start_era)
        end = convert_date_to_integer(advanced.vars.end_date, advanced.vars.end_era)
        if start > end:
            advanced.errors.end_date = 'The End Date of the time period must be later than the Start Date'
