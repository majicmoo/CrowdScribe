from gluon import *
from gluon import BUTTON
import database_transactions as database_transactions
import general_functions as general_functions

class ProjectFunctions:

    def __init__(self, database, db):
        self.database=database
        self.db = db
        self.general_module = general_functions.GeneralFunctions(database, db)


    def check_if_steps_available(self, project_id):

        step2_available = False
        step3_available = False
        step4_available = False

        if project_id is not None:

            if self.database.get_project(project_id) is not None:
                step2_available = True

                if self.database.get_documents_for_project(project_id).first() is not None:
                    step3_available = True

                    if self.database.get_data_fields_for_project(project_id).first() is not None:
                        step4_available = True

        result = {}
        result['2'] = step2_available
        result['3'] = step3_available
        result['4'] = step4_available

        return result


    def retrieve_prepopulated_data_for_create_step_1(self, project_being_edited):
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


    def validate_create_step1(self, form):

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
                    start_date = self.general_module.convert_date_to_integer(current.request.vars.time_period_start_date, current.request.vars.start_era)
            else:
                form.errors.time_period_start_date = "Start Date must not be empty"

            if (current.request.vars.time_period_end_date != "") and (current.request.vars.time_period_end_date != None):
                if date_validator(current.request.vars.time_period_end_date)[1] is not None:
                    form.errors.time_period_end_date = date_validator(current.request.vars.time_period_end_date)[1]
                else:
                    end_date = self.general_module.convert_date_to_integer(current.request.vars.time_period_end_date, current.request.vars.end_era)

            else:
                form.errors.time_period_end_date = "End Date must not be empty"

            if start_date and end_date:
                    if start_date > end_date:
                        form.errors.time_period_end_date = 'The End Date of the time period must be later than the Start Date'

        print form.errors


    def validate_add_image_form(self, form):

        if (current.request.vars.description == "") or (current.request.vars.description is None):
            form.errors.description = "Description must not be empty"

        image_validator = IS_NOT_EMPTY(error_message=("Image must not be left empty"))
        if image_validator(current.request.vars.image)[1] is not None:
            form.errors.image = image_validator(current.request.vars.image)[1]



    def validate_add_field_form(self, form):
        if (current.request.vars.name != "") and (current.request.vars.name is not None):
            form.errors.name = "Name must not be empty"

        if (current.request.vars.short_description != "") and (current.request.vars.short_description is not None):
            form.errors.short_description = "Description must not be empty"


    def attach_number_of_transcriptions(self, documents):
        for document in documents:
            print document
            document.number_of_transcriptions = len(self.database.get_pending_transcriptions_for_document(document.id))
        return documents

    def attach_number_of_transcriptions_to_lists_of_documents(self, all_lists):
        for single_list in all_lists:
            single_list = self.attach_number_of_transcriptions(single_list)
        return all_lists


    def if_none_convert_to_empty_list(self, array):
        if array is None:
            return []
        else:
            return array

    def construct_project_timestring(self, project):
        if project.time_period_start_date:
            timestring = '('+self.general_module.convert_integer_to_date_string(project.time_period_start_date) + " - " +\
                         self.general_module.convert_integer_to_date_string(project.time_period_end_date)+')'
            return timestring
        return ''


    def set_up_project_page_based_on_user(self, project, auth):
        open_documents_with_transcription = open_documents_without_transcription = closed_documents = open_documents\
        = done_documents = []

        if project.author_id == auth._get_user_id():
            # Current user owns project
            # List of documents that have transcription - open - less than 3 transcriptions
            open_documents_with_transcription = self.database.get_open_documents_with_transcription_for_project(project.id)
            open_documents_with_transcription = self.if_none_convert_to_empty_list(open_documents_with_transcription)
            # List of document that don't have a transcription - open
            open_documents_without_transcription = self.database.get_open_documents_without_transcription_for_project(project.id)
            open_documents_without_transcription = self.if_none_convert_to_empty_list(open_documents_without_transcription)
            # List of Complete Document - succesfully transcribed - closed
            closed_documents = self.database.get_closed_documents_for_project(project.id)
            closed_documents = self.if_none_convert_to_empty_list(closed_documents)
            # response.message = 'You own this project'
        else:
            # If not owner
            # Project is not open, redirect
            if project.status != 'Open':
                redirect(URL('default', 'index'))
            open_documents = self.database.get_open_documents_for_project(project.id)
            open_documents = self.if_none_convert_to_empty_list(open_documents)

        # List of done documents - 3 or more transcriptions
        done_documents = self.database.get_done_documents_for_project(project.id)
        done_documents = self.if_none_convert_to_empty_list(done_documents)

        return (open_documents, open_documents_with_transcription, open_documents_without_transcription, done_documents,
        closed_documents)

    def check_if_step1_was_skipped_and_redirect_if_so(self, session):
        if session.project_being_created is not None:
            project_id = session.project_being_created
            project_being_edited = self.database.get_project(project_id)
            return (project_id, project_being_edited)
        else:
            redirect(URL('projects', 'create_step1'))

    def check_if_come_back_from_future_step(self, session):
        project_id = None
        project_being_edited = None
        if session.project_being_created is not None:
            project_id = session.project_being_created
            project_being_edited = self.database.get_project(project_id)
        return (project_id, project_being_edited)


    def create_clear_project_form(self):
        return FORM(DIV(BUTTON("Clear Project", _type='submit', _class='btn btn-danger btn-block',
                                    _onclick="return confirm('Clearing a project will wipe all of your progress."
                                             " Continue?');")))

    def create_next_step_form(self, message):
        return FORM(BUTTON(message, I(_class='icon-arrow-right icon-white'),
                                        _type='submit', _class='btn btn-success btn-block btn-large'))

    def create_previous_step_form(self, message):
        return FORM(BUTTON(message, I(_class='icon-arrow-left icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large btn-left'))

    def process_start_and_end_dates(self):
        if current.request.vars.unknown == "yes":
            start_date = None
            end_date = None
        else:
            start_date = self.general_module.convert_date_to_integer(current.request.vars.time_period_start_date, current.request.vars.start_era)
            end_date = self.general_module.convert_date_to_integer(current.request.vars.time_period_end_date, current.request.vars.end_era)

        return (start_date, end_date)


    def build_transcription_list(self, project, transcriptions):
        i=1
        transcriptions_list = []
        for transcription in transcriptions:
            transcription_dictionary = {}
            transcription_dictionary['number'] = i
            transcription_dictionary['transcription'] = self.database.get_transcribed_fields_for_transcription(transcription.id)
            transcription_dictionary['button'] = A(BUTTON('Accept',_class="btn btn-success"), callback= URL('accept_transcription',
                    vars= dict(document_id=transcription.document_id, transcription_id=transcription.id,
                        project_id=project.id)))
            transcriptions_list.append(transcription_dictionary)
            i += 1

        return transcriptions_list


