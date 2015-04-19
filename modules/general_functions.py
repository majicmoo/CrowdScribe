from gluon import *
import database_transactions as database_transactions

class GeneralFunctions:

    def __init__(self, database, db):
        # database is database_transactions module
        self.database=database
        self.db = db

    def attach_all_information_to_projects(self, projects):
        # Attach a header image, time string and number of transcribed documents to each project in a list.
        projects = self.attach_header_image_to_projects(projects)
        projects  = self.attach_time_string_to_projects(projects)
        projects = self.attach_number_of_transcribed_documents_string_to_projects(projects)

        return projects

    def attach_header_image_to_projects(self, projects):
        # Attach a header image (the image that will be displayed when a project is listed) to each project in a list.
        for project in projects:
            project.header_image = self.database.get_document_for_project_header(project.id).image

        return projects

    def attach_time_string_to_projects(self, projects):
        # Attach a time string to each project in a list e.g. (1900AD-20000AD).
        for project in projects:
            project.timestring = self.construct_project_timestring(project)

        return projects

    def attach_number_of_transcribed_documents_string_to_projects(self, projects):
        # Attach the number of documents that have been transcribed to each project in a list.
        for project in projects:
            project.fraction_transcribed_string = self.construct_number_of_transcribed_documents_string(project.id)

        return projects

    def convert_date_to_integer(self, date, era):
        # Convert a given date and era (eg. 1900 BC) to an integer. BC is negative, AD is positive
        if era =="BC":
            return -int(date)
        else:
            return int(date)

    def convert_integer_to_date_string(self, date):
        # Convert and integer to a date string e.g. 1900 AD
        if date < 0:
            return str(abs(date)) + "BC"
        else:
            return str(abs(date)) + "AD"

    def limit_list_of_projects(self, projects, number):
        # Limit the number of projects returned to the number provided
        if len(projects) < 6:
            projects = projects[0:len(projects)]
        else:
            projects = projects[0:number]

        return projects

    def construct_project_timestring(self, project):
        # Construct a timestring for a project e.g. (1900AD-20000AD).
        if project.time_period_start_date:
            timestring = '('+self.convert_integer_to_date_string(project.time_period_start_date) + " - " +\
                         self.convert_integer_to_date_string(project.time_period_end_date)+')'
            return timestring
        return ''

    def construct_number_of_transcribed_documents_string(self, project_id):
        # Construct number of transcribed documents for a given project.
        number_of_transcribed_documents = self.database.get_number_of_transcribed_documents_for_project(project_id)
        number_documents = len(self.database.get_documents_for_project(project_id))
        return str(number_of_transcribed_documents) + "/" + str(number_documents)

