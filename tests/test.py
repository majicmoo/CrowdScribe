import unittest
import database_transactions as database

from gluon.globals import Request
db = test_db

#execfile("applications/api/controllers/10.py", globals())

#db.commit()

class TestDatabaseTransactions(unittest.TestCase):
    def setUp(self):
        # Clear test_db
        test_db.project.truncate()
        test_db.document_image.truncate()
        test_db.data_field.truncate()
        test_db.transcription.truncate()
        test_db.transcribed_field.truncate()
        test_db.auth_user.truncate()
        test_db.auth_group.truncate()
        test_db.auth_membership.truncate()
        test_db.auth_permission.truncate()
        test_db.auth_event.truncate()
        test_db.auth_cas.truncate()
        test_db.commit()

        # Create User
        self.user_one_id = test_db.auth_user.insert(username='test1')
        self.user_two_id = test_db.auth_user.insert(username='test2')
        # Create Project
        self.project_open_id = test_db.project.insert(name='testproject1', author_id=self.user_one_id, status='Open',
                                                 description='test', tag='History')
        self.project_closed_id = test_db.project.insert(name='testproject2', author_id=self.user_two_id, status='Closed',
                                                 description='test', tag='History')
        # Create Document Image
        self.document_image_id = test_db.document_image.insert(description='test', project_id=self.project_open_id,
                                                               status='Accepted')
        # Create Data Field
        self.data_field_id = test_db.data_field.insert(project_id = self.project_open_id, name = 'test',
                                                   short_description = 'test')
        # Create transcription
        self.transcription_id = test_db.transcription.insert(document_id = self.document_image_id,
                                                              author_id = self.user_two_id, status = 'Open')
        # Create transcription field
        self.transcription_field_id = test_db.transcribed_field.insert(data_field_id = self.data_field_id,
                                                                       transcription_id= self.transcription_id,
                                                                       information='test')
        test_db.commit()

    def test_get_user(self):
        test = database.get_user(db, self.user_one_id)
        user = test.first()
        db.commit()
        self.assertEquals(self.user_one_id, user.id)

    def test_get_all_projects(self):
        test = database.get_all_projects(db)
        project = test.first()
        db.commit()
        self.assertEquals(self.project_open_id, project)

    def test_get_projects_by_user(self):
        test = database.get_projects_by_user(db, self.user_one_id)
        project = test.first()
        db.commit()
        self.assertEquals(self.project_open_id, project)

    def test_get_open_projects_by_user(self):
        test = database.get_open_projects_by_user(db, self.user_one_id)
        project = test.first()
        db.commit()
        self.assertEquals(self.project_open_id, project)
        pass


    def test_get_closed_projects_by_user(self):
        #database.get_closed_projects_by_user(db, user_id)
        pass


    def test_get_project_documents(self):
        #database.get_project_documents(db, user_id)
        pass


    def test_get_project_open_documents(self):
        # database.get_project_open_documents(db, project_id)
        pass


    def test_get_project_closed_documents(self):
        #database.get_project_closed_documents(db, project_id)
        pass


    def test_get_projects_by_tag(self):
        #database.get_projects_by_tag(db, tag)
        pass


    def test_get_projects_by_keyword(self):
        #database.get_projects_by_keyword(db, keyword)
        pass


    def test_get_transcriptions_by_user(self):
        #database.get_transcriptions_by_user(db, user_id)
        pass


    def test_get_transcribed_fields_for_transcription(self):
        #database.get_transcribed_fields_for_transcription(db, transcription_id)
        pass


    def test_get_data_fields_for_project(self):
        #database.get_data_fields_for_project(db, project_id)
        pass


    def test_get_transcriptions_for_document(self):
        #database.get_transcriptions_for_document(db, document_id)
        pass


    def test_get_done_documents_for_user(self):
        #database.get_done_documents_for_user(db, user_id)
        pass


    def test_get_done_documents_for_project(self):
        #database.get_done_documents_for_project(db, project_id)
        pass


    def test_get_documents_for_a_user_that_have_transcription(self):
        #database.get_documents_for_a_user_that_have_transcription(db, user_id)
        pass


    def test_get_documents_for_a_project_that_have_transcription(self):
        #database.get_documents_for_a_project_that_have_transcription(db, project_id)
        pass



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)

