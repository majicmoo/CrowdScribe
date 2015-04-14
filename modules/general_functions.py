from gluon import *
import database_transactions as database_transactions

class GeneralFunctions:

    def __init__(self, database, db):
        self.database=database
        self.db = db

    def attach_header_image_to_projects(self, projects):
        for project in projects:
            project.header_image = self.database.get_document_for_project_header(project.id).image

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

