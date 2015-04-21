from gluon import *
import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import search_functions as search_functions
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)
search_module = search_functions.SearchFunctions(database, db)


def search_results():
    # Controller for displaying users search results
    # Page Title
    response.title = "CrowdScribe | Search Results"

    # Lists for SELECT() helper in advanced search form
    current.tags = ["All", "Sport", "Theatre", "Military", "Journal Entries", "Architecture", "Citizen Information",
                    "Religion", "Art", "Literature", "Finance", "Scientific", "Media", "Music", "Other"]
    eras = ['BC', 'AD']
    orders = ['Alphabetical', 'Earliest', 'Latest']
    # ['Most accepted transcriptions', 'Fewest accepted transcriptions','Nearest completion',
    #  'Farthest from completion']
    
    # Determines if "include unspecified Eras?" is checked or not
    if request.vars.unknown_era is None:
        check = "off"
    else:
        check = "on"
    
    # Creates advanced search form
    advanced = FORM(
        LABEL("Search Text", _for="advancetext"),
        INPUT(_name='advance', _id="advancetext"),
        LABEL("Category", SELECT(current.tags, _name='tag', requires=IS_IN_SET(current.tags))),
        LABEL("Start Date", _for="start_date"),
        INPUT(_id="start_date", _name='start_date', _class='integer', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 2016))),
        LABEL("Start Era", _for="start_era"),
        SELECT(eras, _name='start_era', requires=IS_IN_SET(eras), _id="start_era"),
        LABEL("End Date", _for="end_date"),
        INPUT(_id="end_date", _name='end_date', _class='integer', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 2016))),
        LABEL("End Era", _for="end_era"),
        SELECT(eras, _name='end_era', requires=IS_IN_SET(eras), _id="end_era"),
        LABEL("Include Unspecified Eras?", INPUT(_name='unknown_era', _type='checkbox', checked=check)),
        LABEL("Sort by", SELECT(orders, _name='order', requires=IS_IN_SET(orders))),
        INPUT(_value='Refine search', _type='submit', _id="advancesubmit", _class="btn btn-success"), _method='GET'
    )

    # Start with all open projects in the database as results
    projects = database.get_open_projects()

    # Filter by keyword
    # Gets keywords
    if request.vars.quicksearch is not None:
        searchstr = request.vars.quicksearch
        advanced.vars.advance = request.vars.quicksearch
        
        # Defaults to include unspecified era if navigated from quicksearch
        advanced.vars.unknown_era = "on"
        check = "on"
    elif request.vars.advance is not None:
        searchstr = request.vars.advance
        advanced.vars.advance = request.vars.advance
    else:
        searchstr = None

    # Filter excludes results which do not include any keywords in either project title or description
    if searchstr is not None:
        keywords = searchstr.split(' ')
        projects.exclude(lambda project: search_module.search_project_for_keywords(keywords, project))

    # Filter by category
    if (request.vars.tag != "All") and not search_module.empty_field(request.vars.tag):
        projects.exclude(lambda project: str(request.vars.tag) != str(project.tag))

    # Filter by date
    if not search_module.empty_field(request.vars.start_date):
        start_date = general_module.convert_date_to_integer(request.vars.start_date, request.vars.start_era)
        advanced.vars.start_date = request.vars.start_date
        advanced.vars.start_era = request.vars.start_era
    else:
        # Ensures all dates pass (if validation is fixed)
        start_date = -2016

    if not search_module.empty_field(request.vars.end_date):
        end_date = general_module.convert_date_to_integer(request.vars.end_date, request.vars.end_era)

    else:
        # Ensures all dates pass (if validation is fixed)
        end_date = 2016

    if not search_module.empty_field(request.vars.start_date) or not search_module.empty_field(request.vars.end_date):
        # Excludes unknown dates
        if check == "off":
            # Exclude if end_date is before project's start date, start_date after project's end date or if project
            #  dates are none
            projects.exclude(lambda project: (project.time_period_start_date is None) or
                                             (project.time_period_end_date < start_date) or
                                             (end_date < project.time_period_start_date))

        # Includes unknown dates
        else:
            # Exclude if end_date is before project's start date or start_date after project's end date
            projects.exclude(lambda project: (project.time_period_end_date < start_date) or
                                             (end_date < project.time_period_start_date))
    else:
        if check == "off":
            projects.exclude(lambda project: project.time_period_start_date is None)

    # Order results
    if request.vars.order == 'Earliest':
        # Order by earliest start date
        projects = projects.sort(lambda project: project.time_period_start_date)
    elif request.vars.order == 'Latest':
        # Order by latest end date
        projects = projects.sort(lambda project: project.time_period_end_date, reverse=True)
    else:
        # Order alphabetically (default)
        projects = projects.sort(lambda project: project.name)
    
    advanced.vars = request.vars
    if request.vars.quicksearch is not None:
        advanced.vars.advance = request.vars.quicksearch
        advanced.vars.unknown_era = True

    # Does not validate
    if advanced.process(onvalidation=search_module.date_validator).accepted:
        redirect(URL('search', vars=advanced.vars))
    elif advanced.errors:
        response.flash = 'errors'

    projects = general_module.attach_all_information_to_projects(projects)

    return dict(advanced=advanced, projects=projects, searchstr=searchstr)
