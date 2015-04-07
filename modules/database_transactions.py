from gluon import *
import random
#db = current.db

class DatabaseTransactions:

    def __init__(self, database):
        self.db = database

    # Get User
    def get_user(self, user_id):
        result = self.db(self.db.auth_user.id == user_id).select().first()
        return result

    # Get Project
    def get_project(self, project_id):
        result = self.db(self.db.project.id == project_id).select().first()
        return result

    def get_open_project(self, project_id):
        result = self.db((self.db.project.id == project_id)
                    & (self.db.project.status == "Open")).select().first()
        return result

    def get_all_projects(self):
        result = self.db().select(self.db.project.ALL)
        return result

    def get_open_projects(self):
        result = self.db(self.db.project.status == "Open").select(self.db.project.ALL)
        return result

    def get_projects_for_user(self, user_id):
        result = self.db(self.db.project.author_id == user_id).select()
        return result

    def get_open_projects_for_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Open")).select()
        return result

    def get_open_projects_with_transcriptions_for_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                         & (self.db.document_image.project_id == self.db.project.id)
                         & (self.db.transcription.document_id == self.db.document_image.id)
                         & (self.db.transcription.status == "Pending")
                        & (self.db.project.status == "Open")).select(self.db.project.ALL)
        return result

    def get_open_projects_without_transcriptions_for_user(self, user_id):
        open_projects = self.get_open_projects_for_user(user_id)
        open_projects_with_transcriptions = self.get_open_projects_with_transcriptions_for_user(user_id)
        result = []
        for i in open_projects:
            if i not in open_projects_with_transcriptions:
                result.append(i)
        return result

    def get_under_review_projects_for_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Under Review")).select()
        return result

    def get_closed_projects_for_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Closed")).select()
        return result

    def get_projects_for_tag(self, tag):
        # FIXME: Should this only be open projects?
        result = self.db(self.db.project.tag == tag).select()
        return result

    def get_projects_for_keyword(self, keyword):
        result = self.db(((self.db.project.name.like('%' + keyword + '%')) | (self.db.project.description.like('%' + keyword + '%')))
                    & (self.db.project.status == "Open")).select()
        return result

    def get_random_open_project(self):
        projects = self.get_open_projects()
        index = random.randrange(0, len(projects)-1)
        return projects[index]

    # Get Document
    def get_document(self, document_id):
        result = self.db(self.db.document_image.id == document_id).select().first()
        return result

    def get_documents_for_project(self, project_id):
        result = self.db(self.db.document_image.project_id == project_id).select()
        return result

    def get_open_documents_for_project(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Open")).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_open_documents_with_transcription_for_project(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Open")
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_open_documents_without_transcription_for_project(self, project_id):
        open_documents = self.get_open_documents_for_project(project_id)
        open_documents_with_transcription = self.get_open_documents_with_transcription_for_project(project_id)
        result = []
        for i in open_documents:
            if i not in open_documents_with_transcription:
                result.append(i)
        return result

    def get_closed_documents_for_project(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Closed")).select()
        return result

    def get_done_documents_for_user(self, user_id):
        result = self.db((self.db.document_image.status == "Done")
                    & (self.db.document_image.project_id == self.db.project.id)
                    & (self.db.project.author_id == user_id)).select()
        return result

    def get_done_documents_for_project(self, project_id):
        result = self.db((self.db.document_image.status == "Done")
                    & (self.db.document_image.project_id == project_id)).select()
        return result

    def get_documents_with_transcription_for_project(self, project_id):
        result = self.db((self.db.document_image.project_id == self.db.project.id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select(self.db.document_image.ALL, distinct=True)
        return result

    def get_successfully_transcribed_documents_for_project(self, project_id):
        result = self.db((self.db.document_image.status == "Closed")
                    & (self.db.document_image.project_id == project_id)).select()
        return result

    def get_documents_with_transcription_for_user(self, user_id):
        result = self.db((self.db.document_image.project_id == self.db.project.id)
                    & (self.db.project.author_id == user_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select(self.db.document_image.ALL, distinct=True)
        return result

    def document_has_already_been_transcribed_by_user(self, document_id, user_id):
        result = self.db((self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.document_image.id == document_id)
                    & (self.db.transcription.author_id == user_id)).select()
        print result
        return True if result else False

    # I don't know what purpose this serves and I'm pretty sure its functionality is wrong anyway
    def get_documents_with_transcription_for_project_and_transcription_author(self, project_id, user_id):
        result = self.db((self.db.project.id == self.db.document_image.project_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.project.id == project_id)
                    & (self.db.transcription.author_id == user_id)).select()
        return result

    def get_document_for_project_header(self, project_id):
        result = self.db(self.db.document_image.project_id == project_id).select().first()
        return result


    def get_documents_with_no_transcriptions_for_project(self, project_id):
        has_transcription = self.get_documents_with_transcription_for_project(project_id)
        documents = self.get_documents_for_project(project_id)
        result = []
        for i in documents:
            if i not in has_transcription:
                result.append(i)
        return result

    def get_document_for_transcription(self, transcription_id):
        result = self.db((self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.id == transcription_id)).select(self.db.document_image.ALL, distinct=True)

    # Get Transcriptions
    def get_pending_transcriptions_for_user(self, user_id):
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Pending")).select()
        return result

    def get_accepted_transcriptions_for_user(self, user_id):
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Accepted")).select()
        return result

    def get_rejected_transcriptions_for_user(self, user_id):
        result = self.db((self.db.transcription.author_id == user_id)
                        & (self.db.transcription.document_id == self.db.document_image.id)
                        & (self.db.document_image.project_id == self.db.project.id)
                        & (self.db.transcription.status == "Rejected")).select()
        return result


    def get_transcription(self, transcription_id):
        result = self.db((self.db.transcription.id == transcription_id)).select()
        return result

    def get_transcriptions_for_document(self, document_id):
        result = self.db((self.db.transcription.document_id == document_id)).select()
        return result

    def get_pending_transcriptions_for_document(self, document_id):
        result = self.db((self.db.transcription.document_id == document_id)
                    & (self.db.transcription.status == "Pending")).select()
        return result


    # Get Data Fields
    def get_data_fields_for_project(self, project_id):
        result = self.db(self.db.data_field.project_id == project_id).select()
        return result

    # Get Transcribed Fields
    def get_transcribed_fields_for_transcription(self, transcription_id):
        result = self.db((self.db.transcribed_field.transcription_id == transcription_id)
                    & (self.db.transcribed_field.data_field_id == self.db.data_field.id)).select()
        return result

    # Other
    def project_can_be_closed_for_review(self, project_id):
        done_documents = self.get_done_documents_for_project(project_id)
        if len(done_documents) > 0:
            return True
        open_documents_with_transcription = self.get_open_documents_with_transcription_for_project(project_id)
        if len(open_documents_with_transcription) > 0:
            return True
        return False
