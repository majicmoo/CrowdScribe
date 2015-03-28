from gluon import *
#db = current.db

class DatabaseTransactions:

    def __init__(self, database):
        self.db = database

    def get_user(self, user_id):
        result = self.db(self.db.auth_user.id == user_id).select().first()
        return result


    def get_project(self, project_id):
        result = self.db(self.db.project.id == project_id).select().first()
        return result


    def get_open_project(self, project_id):
        result = self.db((self.db.project.id == project_id)
                    & (self.db.project.status == "Open")).select().first()
        return result

    def get_document(self, document_id):
        result = self.db(self.db.document_image.id == document_id).select().first()
        return result


    def get_all_projects(self, db):
        result = self.db().select(self.db.project.ALL)
        return result

    def get_open_projects(self, db):
        result = self.db(self.db.project.status == "Open").select(self.db.project.ALL)
        return result

    def get_projects_by_user(self, user_id):
        result = self.db(self.db.project.author_id == user_id).select()
        return result


    def get_open_projects_by_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Open")).select()
        return result


    def get_closed_projects_by_user(self, user_id):
        result = self.db((self.db.project.author_id == user_id)
                    & (self.db.project.status == "Closed")).select()
        return result


    def get_project_documents(self, project_id):
        result = self.db(self.db.document_image.project_id == project_id).select()
        return result


    def get_project_open_documents(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Open")).select()
        return result


    def get_project_closed_documents(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.status == "Closed")).select()
        return result


    def get_projects_by_tag(self, tag):
        # FIXME: Should this only be open projects?
        result = self.db(self.db.project.tag == tag).select()
        return result


    def get_projects_by_keyword(self, keyword):
        result = self.db(((self.db.project.name.like('%' + keyword + '%')) | (self.db.project.description.like('%' + keyword + '%')))
                    & (self.db.project.status == "Open")).select()
        return result


    def get_transcriptions_by_user(self, user_id):
        result = self.db(self.db.transcription.author_id == user_id).select()
        return result


    def get_data_fields_for_project(self, project_id):
        result = self.db(self.db.data_field.project_id == project_id).select()
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

    def get_transcribed_fields_for_transcription(self, transcription_id):
        result = self.db((self.db.transcribed_field.transcription_id == transcription_id)
                    & (self.db.transcribed_field.data_field_id == self.db.data_field.id)).select()
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


    def get_documents_for_a_user_that_have_transcription(self, user_id):
        result = self.db((self.db.document_image.project_id == self.db.project.id)
                    & (self.db.project.author_id == user_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select()
        return result


    def get_documents_for_a_project_that_have_transcription(self, project_id):
        result = self.db((self.db.document_image.project_id == project_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.transcription.status == 'Pending')).select()
        return result


    def check_if_document_has_already_been_transcribed_by_user(self, document_id, user_id):
        result = self.db((self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.document_image.id == document_id)
                    & (self.db.transcription.author_id == user_id)).select()
        if result is None:
            return False
        else:
            return True


    def get_documents_in_project_that_has_already_been_transcribed_by_user(self, project_id, user_id):
        result = self.db((self.db.project.id == self.db.document_image.project_id)
                    & (self.db.document_image.id == self.db.transcription.document_id)
                    & (self.db.project.id == project_id)
                    & (self.db.transcription.author_id == user_id)).select()
        return result

    def get_document_image_for_project_header(self, project_id):
        result = self.db(self.db.document_image.project_id == project_id).select().first()
        return result