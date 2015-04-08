from gluon import *
import database_transactions as database_transactions
db = current.db
database = database_transactions.DatabaseTransactions(db)

def attach_header_image_to_projects(projects):
    for project in projects:
        project.header_image = database.get_document_for_project_header(project.id).image

    return projects

def check_if_steps_available(project_id):

    step2_available = False
    step3_available = False
    step4_available = False

    if project_id is not None:

        if database.get_project(project_id) is not None:
            step2_available = True

            if database.get_documents_for_project(project_id).first() is not None:
                step3_available = True

                if database.get_data_fields_for_project(project_id).first() is not None:
                    step4_available = True

    result = {}
    result['2'] = step2_available
    result['3'] = step3_available
    result['4'] = step4_available

    return result




def convert_date_to_integer(date, era):
    if era =="BC":
        return -int(date)
    else:
        return int(date)

def convert_integer_to_date_string(date):
    if date < 0:
        return str(abs(date)) + "BC"
    else:
        return str(abs(date)) + "AD"

def retrieve_prepopulated_data_for_create_step_1(project_being_edited):
    if project_being_edited == None:
        return None
    else:
        data = {}
        data['name'] = project_being_edited.name
        data['description'] = project_being_edited.description
        data['tag'] = project_being_edited.tag
        if project_being_edited.time_period_start_date is None:
            data['start_date'] = ""
            data['end_date'] = ""
            data['start_era'] = 'AD'
            data['end_era'] = 'AD'
            data['unknown'] = "checked"
        else:
            data['unknown'] = "not checked"
            data['start_date'] = abs(project_being_edited.time_period_start_date)
            data['end_date'] = abs(project_being_edited.time_period_end_date)
            if project_being_edited.time_period_start_date < 0:
                data['start_era'] = 'BC'
                if project_being_edited.time_period_end_date < 0:
                    data['end_era'] = 'BC'
                else:
                    data['end_era'] = 'AD'
            else:
                data['start_era'] = 'AD'
                data['end_era'] = 'AD'
        return data


def validate_create_step1(form):

    print current.request.vars

    if (current.request.vars.name == "") or (current.request.vars.name == None):
        form.errors.name = "Name must be entered"

    if (current.request.vars.description == "") or (current.request.vars.description == None):
        form.errors.description = "Description must be entered"

    if (current.request.vars.tag == "") or (current.request.vars.tag == None):
        form.errors.tag = "Tag must be chosen"

    start_date = None
    end_date = None
    date_validator = IS_INT_IN_RANGE(-2015, 2015, error_message ="Date must be whole number between 2015 BC and 2015 AD")

    if current.request.vars.unknown != "yes":
        if (current.request.vars.time_period_start_date != "") and (current.request.vars.time_period_start_date != None):
            if date_validator(current.request.vars.time_period_start_date)[1] is not None:
                form.errors.time_period_start_date = date_validator(current.request.vars.time_period_start_date)[1]
            else:
                start_date = convert_date_to_integer(current.request.vars.time_period_start_date, current.request.vars.start_era)
        else:
            form.errors.time_period_start_date = "Start Date must not be empty"

        if (current.request.vars.time_period_end_date != "") and (current.request.vars.time_period_end_date != None):
            if date_validator(current.request.vars.time_period_end_date)[1] is not None:
                form.errors.time_period_end_date = date_validator(current.request.vars.time_period_end_date)[1]
            else:
                end_date = convert_date_to_integer(current.request.vars.time_period_end_date, current.request.vars.end_era)

        else:
            form.errors.time_period_end_date = "End Date must not be empty"

        if start_date and end_date:
                if start_date > end_date:
                    form.errors.time_period_end_date = 'The End Date of the time period must be later than the Start Date'

    print form.errors
