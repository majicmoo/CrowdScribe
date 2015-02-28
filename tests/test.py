import unittest
import database_transactions as database

db = test_db


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

        # Setup statuses
        self.open_status = 'Open'
        self.closed_status = 'Closed'

        # Setup tags
        self.tag_one = 'Sports'
        self.tag_two = 'Literature'

        # Setup keywords
        self.keyword = 'test'

        # Create User
        self.user_one_id = test_db.auth_user.insert(username='test1')
        self.user_two_id = test_db.auth_user.insert(username='test2')
        # Create Project
        self.project_one = test_db.project.insert(name='testproject1', author_id=self.user_one_id,
                                                      status=self.open_status, description='test', tag=self.tag_one)
        self.project_two = test_db.project.insert(name='testproject2', author_id=self.user_two_id,
                                                        status=self.closed_status, description='test', tag=self.tag_one)

        # Setting up projects for get project by keyword test
        # Keyword in description
        self.project_three = test_db.project.insert(name='project1', author_id=self.user_one_id, status=self.open_status,
                                                      description='test', tag=self.tag_two)
        # Keyword in name
        self.project_four = test_db.project.insert(name='testproject1', author_id=self.user_one_id, status=self.open_status,
                                                      description='nothing', tag=self.tag_two)

        # Create Document Image
        self.document_image_open_id = test_db.document_image.insert(description='test',
                                                                    project_id=self.project_one, status=self.open_status)
        self.document_image_closed_id = test_db.document_image.insert(description='test',
                                                                      project_id=self.project_one, status=self.closed_status)
        # Create Data Field
        self.data_field_id = test_db.data_field.insert(project_id=self.project_one, name='test',
                                                       short_description='test')
        # Create transcription
        self.transcription_open_id = test_db.transcription.insert(document_id=self.document_image_open_id,
                                                                  author_id=self.user_two_id, status=self.open_status)
        self.transcription_closed_id = test_db.transcription.insert(document_id=self.document_image_open_id,
                                                                    author_id=self.user_two_id, status=self.closed_status)
        # Create transcription field
        self.transcription_field_id = test_db.transcribed_field.insert(data_field_id=self.data_field_id,
                                                                       transcription_id=self.transcription_open_id,
                                                                       information='test')
        test_db.commit()



        # Set up variables

        # Number of projects
        self.total_number_of_projects = 4
        self.total_number_of_open_projects = 3
        self.total_number_of_closed_projects = 3

        # Number of user projects by user
        self.total_number_of_user_one_projects = 3
        self.total_number_of_user_two_projects = 1

        # Number of open user projects by user
        self.total_number_of_user_one_open_projects = 3
        self.total_number_of_user_two_open_projects = 0

        # Number of closed user projects by user
        self.total_number_of_user_one_closed_projects = self.total_number_of_user_one_projects - \
                                                        self.total_number_of_user_one_open_projects
        self.total_number_of_user_two_closed_projects = self.total_number_of_user_two_projects - \
                                                        self.total_number_of_user_two_open_projects

        # Total number of documents for a project
        self.total_number_of_documents_for_project_one = 2
        self.total_number_of_documents_for_project_two = 0
        self.total_number_of_documents_for_project_three = 0
        self.total_number_of_documents_for_project_four = 0

        # Total number of open project documents for a project
        self.total_number_of_open_documents_for_project_one = 1
        self.total_number_of_open_documents_for_project_two = 0
        self.total_number_of_open_documents_for_project_three = 0
        self.total_number_of_open_documents_for_project_four = 0

        # Total number of closed project documents for a project
        self.total_number_of_closed_documents_for_project_one = self.total_number_of_documents_for_project_one - \
                                                                self.total_number_of_open_documents_for_project_one
        self.total_number_of_closed_documents_for_project_two = self.total_number_of_documents_for_project_two - \
                                                                self.total_number_of_open_documents_for_project_two
        self.total_number_of_closed_documents_for_project_three = self.total_number_of_documents_for_project_three - \
                                                                self.total_number_of_open_documents_for_project_three
        self.total_number_of_closed_documents_for_project_four = self.total_number_of_documents_for_project_four - \
                                                                self.total_number_of_open_documents_for_project_four
        # Number of projects with tags
        self.total_number_of_projects_with_tag_one = 2
        self.total_number_of_projects_with_tag_two = 2

        # Number of open projects with tags
        self.total_number_of_open_projects_with_tag_one = 1
        self.total_number_of_open_projects_with_tag_two = 2

        # Number of open projects with keyword test
        self.total_number_of_open_projects_with_keyword = 3

        # Number of transcriptions by users
        self.total_number_of_transcriptions_for_user_one = 0
        self.total_number_of_transcriptions_for_user_two = 2

        # Number of open transcriptions by users
        self.total_number_of_open_transcriptions_for_user_one = 0
        self.total_number_of_open_transcriptions_for_user_two = 1

        # Number of closed transcriptions by users
        self.total_number_of_closed_transcriptions_for_user_one = self.total_number_of_transcriptions_for_user_one - \
                                                                  self.total_number_of_open_transcriptions_for_user_one
        self.total_number_of_closed_transcriptions_for_user_two = self.total_number_of_transcriptions_for_user_two - \
                                                                  self.total_number_of_open_transcriptions_for_user_two


    def test_get_user(self):
        test = database.get_user(db, self.user_one_id)
        user = test.first()
        self.assertEquals(self.user_one_id, user.id)

    def test_get_all_projects(self):
        projects = database.get_all_projects(db)
        no_of_projects = len(projects)
        self.assertEquals(self.total_number_of_projects, no_of_projects)

    def test_get_projects_by_user(self):
        user_one_projects = database.get_projects_by_user(db, self.user_one_id)
        user_two_projects = database.get_projects_by_user(db, self.user_two_id)
        for i in user_one_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_one_id.username)
        for i in user_two_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_two_id.username)
        # Check that correct number of projects are returned
        self.assertEquals(self.total_number_of_user_one_projects, len(user_one_projects))
        self.assertEquals(self.total_number_of_user_two_projects, len(user_two_projects))

    def test_get_open_projects_by_user(self):
        user_one_projects = database.get_open_projects_by_user(db, self.user_one_id)
        user_two_projects = database.get_open_projects_by_user(db, self.user_two_id)
        for i in user_one_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_one_id.username)
            # Check all projects are open
            self.assertEquals(i.status, self.open_status)
        for i in user_two_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_two_id.username)
            # Check all projects are open
            self.assertEquals(i.status, self.open_status)

        # Check that correct number of projects are returned
        self.assertEquals(self.total_number_of_user_one_open_projects, len(user_one_projects))
        self.assertEquals(self.total_number_of_user_two_open_projects, len(user_two_projects))

    def test_get_closed_projects_by_user(self):
        user_one_projects = database.get_closed_projects_by_user(db, self.user_one_id)
        user_two_projects = database.get_closed_projects_by_user(db, self.user_two_id)
        for i in user_one_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_one_id.username)
            # Check all projects are closed
            self.assertEquals(i.status, self.closed_status)
        for i in user_two_projects:
            # Check all projects returned have correct username
            self.assertEquals(i.author_id.username, self.user_two_id.username)
            # Check all projects are closed
            self.assertEquals(i.status, 'Closed')
        # Check that correct number of projects are returned
        self.assertEquals(self.total_number_of_user_one_closed_projects, len(user_one_projects))
        self.assertEquals(self.total_number_of_user_two_closed_projects, len(user_two_projects))

    def test_get_project_documents(self):
        project_one_documents = database.get_project_documents(db, self.project_one)
        project_two_documents = database.get_project_documents(db, self.project_two)
        project_three_documents = database.get_project_documents(db, self.project_three)
        project_four_documents = database.get_project_documents(db, self.project_four)
        for i in project_one_documents:
            self.assertEquals(i.project_id, self.project_one.id)
        for i in project_two_documents:
            self.assertEquals(i.project_id, self.project_two.id)
        for i in project_three_documents:
            self.assertEquals(i.project_id, self.project_three.id)
        for i in project_four_documents:
            self.assertEquals(i.project_id, self.project_four.id)
        self.assertEquals(self.total_number_of_documents_for_project_one, len(project_one_documents))
        self.assertEquals(self.total_number_of_documents_for_project_two, len(project_two_documents))
        self.assertEquals(self.total_number_of_documents_for_project_three, len(project_three_documents))
        self.assertEquals(self.total_number_of_documents_for_project_four, len(project_four_documents))

    def test_get_project_open_documents(self):
        project_one_documents = database.get_project_open_documents(db, self.project_one)
        project_two_documents = database.get_project_open_documents(db, self.project_two)
        project_three_documents = database.get_project_open_documents(db, self.project_three)
        project_four_documents = database.get_project_open_documents(db, self.project_four)
        for i in project_one_documents:
            self.assertEquals(i.project_id, self.project_one.id)
             # Check open
            self.assertEquals(i.status, self.open_status)
        for i in project_two_documents:
            self.assertEquals(i.project_id, self.project_two.id)
             # Check open
            self.assertEquals(i.status, self.open_status)
        for i in project_three_documents:
            self.assertEquals(i.project_id, self.project_three.id)
             # Check open
            self.assertEquals(i.status, self.open_status)
        for i in project_four_documents:
            self.assertEquals(i.project_id, self.project_four.id)
             # Check open
            self.assertEquals(i.status, self.open_status)

        self.assertEquals(self.total_number_of_open_documents_for_project_one, len(project_one_documents))
        self.assertEquals(self.total_number_of_open_documents_for_project_two, len(project_two_documents))
        self.assertEquals(self.total_number_of_open_documents_for_project_three, len(project_three_documents))
        self.assertEquals(self.total_number_of_open_documents_for_project_four, len(project_four_documents))

    def test_get_project_closed_documents(self):
        project_one_documents = database.get_project_closed_documents(db, self.project_one)
        project_two_documents = database.get_project_closed_documents(db, self.project_two)
        project_three_documents = database.get_project_closed_documents(db, self.project_three)
        project_four_documents = database.get_project_closed_documents(db, self.project_four)
        for i in project_one_documents:
            self.assertEquals(i.project_id, self.project_one.id)
             # Check closed
            self.assertEquals(i.status, self.closed_status)
        for i in project_two_documents:
            self.assertEquals(i.project_id, self.project_two.id)
             # Check closed
            self.assertEquals(i.status, self.closed_status)
        for i in project_three_documents:
            self.assertEquals(i.project_id, self.project_three.id)
             # Check closed
            self.assertEquals(i.status, self.closed_status)
        for i in project_four_documents:
            self.assertEquals(i.project_id, self.project_four.id)
             # Check closed
            self.assertEquals(i.status, self.closed_status)

        self.assertEquals(self.total_number_of_closed_documents_for_project_one, len(project_one_documents))
        self.assertEquals(self.total_number_of_closed_documents_for_project_two, len(project_two_documents))
        self.assertEquals(self.total_number_of_closed_documents_for_project_three, len(project_three_documents))
        self.assertEquals(self.total_number_of_closed_documents_for_project_four, len(project_four_documents))

    def test_get_projects_by_tag(self):
        tag_one_projects = database.get_projects_by_tag(db, self.tag_one)
        tag_two_projects = database.get_projects_by_tag(db, self.tag_two)
        for i in tag_one_projects:
            self.assertEquals(i.tag, self.tag_one)
        for i in tag_two_projects:
            self.assertEquals(i.tag, self.tag_two)
        self.assertEquals(len(tag_one_projects), self.total_number_of_projects_with_tag_one)
        self.assertEquals(len(tag_two_projects), self.total_number_of_projects_with_tag_two)

    def test_get_projects_by_keyword(self):
        projects = database.get_projects_by_keyword(db, self.keyword)
        for i in projects:
            if self.keyword in i.description:
                self.assertIn(self.keyword, i.description)
                break
            self.assertIn(self.keyword, i.name)
        self.assertEquals(self.total_number_of_open_projects_with_keyword, len(projects))

    def test_get_transcriptions_by_user(self):
        user_one_transcriptions = database.get_transcriptions_by_user(db, self.user_one_id)
        user_two_transcriptions = database.get_transcriptions_by_user(db, self.user_two_id)
        for i in user_one_transcriptions:
            self.assertEquals(i.author_id, self.user_one_id)
        for i in user_two_transcriptions:
            self.assertEquals(i.author_id, self.user_two_id)
        self.assertEquals(self.total_number_of_transcriptions_for_user_one, len(user_one_transcriptions))
        self.assertEquals(self.total_number_of_transcriptions_for_user_two, len(user_two_transcriptions))

    def test_get_transcribed_fields_for_transcription(self):
        target_number_of_documents = 1
        transcribed_fields = database.get_transcribed_fields_for_transcription(db, self.transcription_open_id)
        for i in transcribed_fields:
            # Check right transcription ID
            self.assertEquals(i.transcription_id, self.transcription_open_id)
        # Check correct number is returned
        self.assertEquals(target_number_of_documents, len(transcribed_fields))

    def test_get_data_fields_for_project(self):
        target_number_of_documents = 1
        data_fields = database.get_data_fields_for_project(db, self.project_one)
        for i in data_fields:
            self.assertEquals(i.project_id, self.project_one)
        self.assertEquals(target_number_of_documents, len(data_fields))

    def test_get_transcriptions_for_document(self):
        # FIXME: Doesn't have i.document_id
        # target_number_of_documents = 1
        # transcriptions = database.get_transcriptions_for_document(db, self.document_image_open_id)
        # for i in transcriptions:
        #     print i
        #     self.assertEquals(i.document_id, self.document_image_open_id)
        # self.assertEquals(target_number_of_documents, len(transcriptions))
        pass

    def test_get_done_documents_for_user(self):
        # FIXME: What are done documents?
        # documents = database.get_done_documents_for_user(db, user_id)
        pass

    def test_get_done_documents_for_project(self):
        # database.get_done_documents_for_project(db, project_id)
        pass

    def test_get_documents_for_a_user_that_have_transcription(self):
        # Documents user own and have a transcription
        documents = database.get_documents_for_a_user_that_have_transcription(db, self.user_one_id)
        for i in documents:
            self.assertEquals(i.project.author_id, self.user_one_id)

    def test_get_documents_for_a_project_that_have_transcription(self):
        # FIXME: Not sure if the database transaction works for this one
        pass
        # documents = database.get_documents_for_a_project_that_have_transcription(db, self.project_open_id)
        # for i in documents:
        #     print i
        #     self.assertEquals(i.document_image.project_id, self.project_open_id)
        #     self.assertTrue(self.exists(i.transcription.id))

    def exists(self, x):
        try:
            x
        except NameError:
            return False
        else:
            return True


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)
