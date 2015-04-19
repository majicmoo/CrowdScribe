from gluon import *
import random
#db = current.db

class DatabaseTransactions:

    def __init__(self, database):
        self.db = database

    ######################################### Get User ################################################################
    def get_user(self, user_id):
        # Get User from user_id
        result = self.db(self.db.auth_user.id == user_id).select().first()
        return result

    ########################################## Get Projects##########################################################
    def get_project(self, project_id):
        # Get project from project id
        result = self.db(self.db.project.id == project_id).select().first()
        return result

    def get_open_project(self, project_id):
        # Get project from id, if open
        result = self.db((self.db.project.id == project_id)
                    & (self.db.project.status == "Open")).select().first()
        return result

    def get_all_projects(self):
        # Get all projects in database
        result = self.db().select(self.db.project.ALL)
        return result

    def get_open_projects(self):
        # Get all open projects in database
        result = self.db(self.db.project.status == "Open").select(self.db.project.ALL)
        return result

    def get_projects_for_user(self, user_id):
        # Get all projects belonging to a user
        result = self.db(self.db.project.author_id == user_id).select()
        return result

    def get_open_projects_for_user(self, user_id):
        # Get all open projects for a user
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Open")).select()
        return result

    def get_open_projects_with_transcriptions_for_user(self, user_id):
        # Get all open projects with transcriptions for a user
        result = self.db((self.db.project.author_id == user_id)
                         & (self.db.document_image.project_id == self.db.project.id)
                         & (self.db.transcription.document_id == self.db.document_image.id)
                         & (self.db.transcription.status == "Pending")
                        & (self.db.project.status == "Open")).select(self.db.project.ALL, distinct=True)
        return result

    def get_open_projects_without_transcriptions_for_user(self, user_id):
        # Get open projects without transcriptions for a user
        open_projects = self.get_open_projects_for_user(user_id)
        open_projects_with_transcriptions = self.get_open_projects_with_transcriptions_for_user(user_id)
        result = []
        for i in open_projects:
            if i not in open_projects_with_transcriptions:
                result.append(i)
        return result

    def get_under_review_projects_for_user(self, user_id):
        # Get a project that is under review for a user
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Under Review")).select()
        return result

    def get_closed_projects_for_user(self, user_id):
        # Get all closed projects that a user owns
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Closed")).select()
        return result

    def get_projects_for_tag(self, tag):
        # Get all projects with a certain tag
        result = self.db((self.db.project.tag == tag) & (self.db.project.status == "Open")).select()
        return result

    def get_projects_for_keyword(self, keyword):
        # Get all projects with a given keyword in the description or title
        result = self.db(((self.db.project.name.like('%' + keyword + '%')) | (self.db.project.description.like('%' + keyword + '%')))
                    & (self.db.project.status == "Open")).select()
        return result

    def get_random_open_project(self):
        # Get a random open project
        projects = self.get_open_projects()
        index = random.randrange(0, len(projects)-1)
        return projects[index]

    def get_number_of_transcribed_documents_for_project(self, project_id):
        # Get the number of transcribed documents for a given project
        documents = self.db((self.db.project.id == self.db.document_image.project_id)
                            & (self.db.project.id == project_id)).select(self.db.document_image.ALL)
        result = 0
        for document in documents:
            if document.status == "Closed":
                result += 1
        return result

    def get_latest_projects(self):
        # Get the most recently created projects
        result = self.db(self.db.project.status == "Open")\
                .select(orderby=~(self.db.project.date_created), limitby = (0,6))
        return result

    def get_most_transcribed_projects(self):
        # Get the projects with the most successfully transcribed documents
        all_projects = self.get_open_projects()
        for project in all_projects:
            project.number_transcribed = self.get_number_of_transcribed_documents_for_project(project.id)

        all_projects = all_projects.sort(lambda project: project.number_transcribed, reverse=True)
        result=all_projects

        return result

    ########################################## Get Documents#########################################################
    def get_document(self, document_id):
        # Get a document by its id
        result = self.db(self.db.document_image.id == document_id).select().first()
        return result

    def get_documents_for_project(self, project_id):
        # Get all documents for a project
        result = self.db(self.db.document_image.project_id == project_id).select()
        return result

    def get_open_documents_for_project(self, project_id):
        # Get all open documents for a project
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Open")).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_open_documents_with_transcription_for_project(self, project_id):
        # Get all open documents with transcription for a given project
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Open")
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_open_documents_without_transcription_for_project(self, project_id):
        # Get all open documents without transcriptions for a given project
        open_documents = self.get_open_documents_for_project(project_id)
        open_documents_with_transcription = self.get_open_documents_with_transcription_for_project(project_id)
        result = []
        for i in open_documents:
            if i not in open_documents_with_transcription:
                result.append(i)
        return result

    def get_closed_documents_for_project(self, project_id):
        # Get all closed documents for a project
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Closed")).select()
        return result

    def get_done_documents_for_user(self, user_id):
        # Get all done documents for a user
        result = self.db((self.db.document_image.status == "Done")
                    & (self.db.document_image.project_id == self.db.project.id)
                    & (self.db.project.author_id == user_id)).select()
        return result

    def get_done_documents_for_project(self, project_id):
        # Get all done documents for a project
        result = self.db((self.db.document_image.status == "Done")
                    & (self.db.document_image.project_id == project_id)).select()
        return result

    def get_documents_with_transcription_for_project(self, project_id):
        # Get all documents with transcription for a project
        result = self.db((self.db.document_image.project_id == self.db.project.id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')
                    &(self.db.document_image.project_id == project_id)).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_successfully_transcribed_documents_for_project(self, project_id):
        # Get all successfully transcribed documents for a project
        result = self.db((self.db.document_image.status == "Closed")
                    & (self.db.document_image.project_id == project_id)).select()
        return result

    def get_documents_with_transcription_for_user(self, user_id):
        # Get all documents with one or more transcriptions for a user
        result = self.db((self.db.document_image.project_id == self.db.project.id)
                    & (self.db.project.author_id == user_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select(self.db.document_image.ALL, distinct=True)
        return result

    def document_has_already_been_transcribed_by_user(self, document_id, user_id):
        # Return true if a document has already been transcribed by a user, otherwise false
        result = self.db((self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.document_image.id == document_id)
                    & (self.db.transcription.author_id == user_id)
                    & (self.db.transcription.status == "Pending")).select()
        return True if result else False

    # FIXME: BAD NAMING ALSO CAN PROBABLY BE HANDELED BY ANOTHER FUNCTION
    def document_transcribed_by_user(self, document_id, user_id):
        result = self.db((self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.document_image.id == document_id)
                    & (self.db.transcription.author_id == user_id)).select()
        return result


    def get_documents_with_transcription_for_project_and_transcription_author(self, project_id, user_id):
        # Get all documents with a transcription for a project and the transcription author
        result = self.db((self.db.project.id == self.db.document_image.project_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.project.id == project_id)
                    & (self.db.transcription.author_id == user_id)).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_document_for_project_header(self, project_id):
        # Get a document for the header image of a project
        result = self.db(self.db.document_image.project_id == project_id).select().first()
        return result


    def get_documents_with_no_transcriptions_for_project(self, project_id):
        # Get all documents with no transcriptions for a project
        has_transcription = self.get_documents_with_transcription_for_project(project_id)
        documents = self.get_documents_for_project(project_id)
        result = []
        for i in documents:
            if i not in has_transcription:
                result.append(i)
        return result

    def get_document_for_transcription(self, transcription_id):
        #FIXME: Doesn't work
        result = self.db((self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.id == transcription_id)).select(self.db.document_image.ALL, distinct=True).first()
        return result


   ########################################## Get Transcriptions####################################################
    def get_pending_transcriptions_for_user(self, user_id):
        # Get pending transcriptions for its author
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Pending")).select()
        return result

    def get_accepted_transcriptions_for_user(self, user_id):
        # Get accepted transcriptions for its author
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Accepted")).select()
        return result

    def get_rejected_transcriptions_for_user(self, user_id):
        # Get rejected transcriptions for its author
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Rejected")).select()
        return result

    def get_username_for_transcription(self, transcription_id):
        transcription = self.get_transcription(transcription_id)
        result = transcription.author_id.username
        return result


    def get_transcription(self, transcription_id):
        # Get a transcription by its id
        result = self.db((self.db.transcription.id == transcription_id)).select().first()
        return result

    def get_transcriptions_for_document(self, document_id):
        # Get all transcriptions for a document
        result = self.db((self.db.transcription.document_id == document_id)).select()
        return result

    def get_transcriptions_for_user_and_document(self, document_id, user_id):
        # Get all transcriptions by a document and the user who is the auther of the transcriptions
        result = self.db((self.db.transcription.document_id == document_id) & (self.db.transcription.author_id == user_id)).select().first()
        return result

    def get_pending_transcriptions_for_document(self, document_id):
        # Get all pending transcriptions for a document
        result = self.db((self.db.transcription.document_id == document_id)
                    & (self.db.transcription.status == "Pending")).select()
        return result

    def get_accepted_transcription_for_document(self, document_id):
        # Get all accepted transcriptions for a document
        result = self.db((self.db.transcription.document_id == document_id)
                    & (self.db.transcription.status == "Accepted")).select().first()
        return result


    ########################################## Get Data Fields####################################################
    def get_data_fields_for_project(self, project_id):
        # Get all data fields for a project
        result = self.db(self.db.data_field.project_id == project_id).select()
        return result

    ########################################## Get Transcribed Fields#############################################
    def get_transcribed_fields_for_transcription(self, transcription_id):
        # Get all transcribed fields for a transcription
        result = self.db((self.db.transcribed_field.transcription_id == transcription_id)
                    & (self.db.transcribed_field.data_field_id == self.db.data_field.id)).select()
        return result

    ########################################## Other##############################################################
    def project_can_be_closed_for_review(self, project_id):
        # Return True if a project can be closed for review, else false
        done_documents = self.get_done_documents_for_project(project_id)
        if len(done_documents) > 0:
            return True
        open_documents_with_transcription = self.get_open_documents_with_transcription_for_project(project_id)
        if len(open_documents_with_transcription) > 0:
            return True
        return False
