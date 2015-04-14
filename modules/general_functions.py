from gluon import *
import database_transactions as database_transactions

class GeneralFunctions:

    def __init__(self, database, db):
        self.database=database
        self.db = db

    def attach_all_information_to_projects(self, projects):
        projects = self.attach_header_image_to_projects(projects)
        projects  = self.attach_time_string_to_projects(projects)
        projects = self.attach_number_of_transcribed_documents_string_to_projects(projects)

        return projects

    def attach_header_image_to_projects(self, projects):
        for project in projects:
            project.header_image = self.database.get_document_for_project_header(project.id).image

        return projects

    def attach_time_string_to_projects(self, projects):
        for project in projects:
            project.timestring = self.construct_project_timestring(project)

        return projects

    def attach_number_of_transcribed_documents_string_to_projects(self, projects):
        for project in projects:
            project.fraction_transcribed_string = self.construct_number_of_transcribed_documents_string(project.id)

        return projects

    def convert_date_to_integer(self, date, era):
        if era =="BC":
            return -int(date)
        else:
            return int(date)

    def convert_integer_to_date_string(self, date):
        if date < 0:
            return str(abs(date)) + "BC"
        else:
            return str(abs(date)) + "AD"

    def limit_list_of_projects(self, projects, number):
        if len(projects) < 6:
            projects = projects[0:len(projects)]
        else:
            projects = projects[0:number]

        return projects

    def construct_project_timestring(self, project):
        if project.time_period_start_date:
            timestring = '('+self.convert_integer_to_date_string(project.time_period_start_date) + " - " +\
                         self.convert_integer_to_date_string(project.time_period_end_date)+')'
            return timestring
        return ''

    def construct_number_of_transcribed_documents_string(self, project_id):
        number_of_transcribed_documents = self.database.get_number_of_transcribed_documents_for_project(project_id)
        number_documents = len(self.database.get_documents_for_project(project_id))
        return str(number_of_transcribed_documents) + "/" + str(number_documents)

