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
        self.project_closed_id = test_db.project.insert(name='testproject2', author_id=self.user_two_id,
                                                        status='Closed', description='test', tag='History')
        # Create Document Image
        self.document_image_open_id = test_db.document_image.insert(description='test',
                                                                    project_id=self.project_open_id, status='Open')
        self.document_image_closed_id = test_db.document_image.insert(description='test',
                                                                      project_id=self.project_open_id, status='Closed')
        # Create Data Field
        self.data_field_id = test_db.data_field.insert(project_id=self.project_open_id, name='test',
                                                       short_description='test')
        # Create transcription
        self.transcription_open_id = test_db.transcription.insert(document_id=self.document_image_open_id,
                                                                  author_id=self.user_two_id, status='Open')
        self.transcription_closed_id = test_db.transcription.insert(document_id=self.document_image_open_id,
                                                                    author_id=self.user_two_id, status='Closed')
        # Create transcription field
        self.transcription_field_id = test_db.transcribed_field.insert(data_field_id=self.data_field_id,
                                                                       transcription_id=self.transcription_open_id,
                                                                       information='test')
        test_db.commit()

    def test_get_user(self):
        test = database.get_user(db, self.user_one_id)
        user = test.first()
        self.assertEquals(self.user_one_id, user.id)

    def test_get_all_projects(self):
        target_no_of_projects = 2
        projects = database.get_all_projects(db)
        no_of_projects = len(projects)
        self.assertEquals(target_no_of_projects, no_of_projects)

    def test_get_projects_by_user(self):
        target_no_of_projects = 1
        target_username = 'test1'
        projects = database.get_projects_by_user(db, self.user_one_id)
        for i in projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, target_username)
        # Check that correct number of projects are returned
        self.assertEquals(target_no_of_projects, len(projects))

    def test_get_open_projects_by_user(self):
        target_no_of_projects = 1
        target_username = 'test1'
        projects = database.get_open_projects_by_user(db, self.user_one_id)
        for i in projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, target_username)
            # Check all projects are open
            self.assertEquals(i.status, 'Open')
        # Check that correct number of projects are returned
        self.assertEquals(target_no_of_projects, len(projects))

    def test_get_closed_projects_by_user(self):
        target_no_of_projects = 1
        target_username = 'test2'
        projects = database.get_closed_projects_by_user(db, self.user_two_id)
        for i in projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, target_username)
            # Check all projects are closed
            self.assertEquals(i.status, 'Closed')
        # Check that correct number of projects are returned
        self.assertEquals(target_no_of_projects, len(projects))

    def test_get_project_documents(self):
        target_number_of_project_documents = 2
        project_documents = database.get_project_documents(db, self.project_open_id)
        self.assertEquals(target_number_of_project_documents, len(project_documents))

    def test_get_project_open_documents(self):
        target_number_of_documents = 1
        open_documents = database.get_project_open_documents(db, self.project_open_id)
        for i in open_documents:
            # Check right project
            self.assertEquals(i.project_id, self.project_open_id)
            # Check open
            self.assertEquals(i.status, 'Open')
        # Check that correct number of projects are returned
        self.assertEquals(target_number_of_documents, len(open_documents))


    def test_get_project_closed_documents(self):
        target_number_of_documents = 1
        closed_documents = database.get_project_closed_documents(db, self.project_open_id)
        for i in closed_documents:
            # Check right project
            self.assertEquals(i.project_id, self.project_open_id)
            # Check open
            self.assertEquals(i.status, 'Closed')
        # Check that correct number of projects are returned
        self.assertEquals(target_number_of_documents, len(closed_documents))

    def test_get_projects_by_tag(self):
        target_number_of_documents = 2
        tag = 'History'
        projects = database.get_projects_by_tag(db, tag)
        for i in projects:
            self.assertEquals(i.tag, tag)
        self.assertEquals(len(projects), target_number_of_documents)


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

