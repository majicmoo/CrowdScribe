import unittest
import general_functions
import database_transactions
db = test_db
database = database_transactions.DatabaseTransactions(db)
functions = general_functions.GeneralFunctions(database, db)


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
        # Document
        self.open_status = 'Open'
        self.closed_status = 'Closed'
        self.done_status = 'Done'
        self.under_review_status = 'Under Review'
        # Transcriptions
        self.pending_status = 'Pending'
        self.accepted_status = 'Accepted'
        self.rejected_status = 'Rejected'

        # Setup tags
        self.tag_one = 'Sports'
        self.tag_two = 'Literature'

        # Users
        self.user_one = test_db.auth_user.insert(username="user_one")

        # Projects
        self.project_one = test_db.project.insert(name="project_one", author_id=self.user_one, status=self.open_status,
                                                  description="description_one", tag=self.tag_one,
                                                  time_period_start_date = 1900, time_period_end_date = 2000)
        self.project_two = test_db.project.insert(name="project_two", author_id=self.user_one, status=self.open_status,
                                                  description="description_two", tag=self.tag_one,
                                                  time_period_start_date = 1800, time_period_end_date = 1850)
        self.projects = [self.project_one, self.project_two]

        # Documents
        self.document_one = test_db.document_image.insert(description="description_one", image="temp",
                                                          project_id=self.project_one, status=self.open_status)
        self.document_two = test_db.document_image.insert(description="description_two", image="temp",
                                                          project_id=self.project_two, status=self.closed_status)




     # TESTS GENERAL FUNCTIONS ####################################################################

    def test_attach_all_information_to_projects(self):
        functions.attach_all_information_to_projects(self.projects)
        self.assertEquals(self.projects[0].header_image, 'temp')
        self.assertEquals(self.projects[0].timestring, '(1900AD - 2000AD)')
        self.assertEquals(self.projects[0].fraction_transcribed_string, '0/1')

        self.assertEquals(self.projects[1].header_image, 'temp')
        self.assertEquals(self.projects[1].timestring, '(1800AD - 1850AD)')
        self.assertEquals(self.projects[1].fraction_transcribed_string, '1/1')

    def test_attach_header_image_to_projects(self):
        functions.attach_header_image_to_projects(self.projects)
        for project in self.projects:
            self.assertEquals(project.header_image,"temp")

    def test_attach_time_string_to_projects(self):
        functions.attach_time_string_to_projects(self.projects)
        self.assertEquals(self.projects[0].timestring, '(1900AD - 2000AD)')
        self.assertEquals(self.projects[1].timestring, '(1800AD - 1850AD)')

    def test_attach_number_of_transcribed_documents_string_to_projects(self):
        functions.attach_number_of_transcribed_documents_string_to_projects(self.projects)
        self.assertEquals(self.projects[0].fraction_transcribed_string, '0/1')
        self.assertEquals(self.projects[1].fraction_transcribed_string, '1/1')

    def test_convert_date_to_integer(self):
        date = functions.convert_date_to_integer('1900','AD')
        self.assertEquals(date, 1900)
        date = functions.convert_date_to_integer('1900','BC')
        self.assertEquals(date, -1900)

    def test_convert_integer_to_date_string(self):
        date = functions.convert_integer_to_date_string(1900)
        self.assertEquals(date, '1900AD')
        date = functions.convert_integer_to_date_string(-1900)
        self.assertEquals(date, '1900BC')

    def test_limit_list_of_projects(self):
        temp_projects = [1,2,3,4,5,6,7,8,9,10]
        new_projects = functions.limit_list_of_projects(temp_projects, 6)
        self.assertEquals(len(new_projects), 6)

        temp_projects = [1,2,3,4,5]
        new_projects = functions.limit_list_of_projects(temp_projects, 6)
        self.assertEquals(len(new_projects), 5)


    def test_construct_project_timestring(self):
        timestring = functions.construct_project_timestring(self.project_one)
        self.assertEquals(timestring, '(1900AD - 2000AD)')
        timestring = functions.construct_project_timestring(self.project_two)
        self.assertEquals(timestring, '(1800AD - 1850AD)')

    def test_construct_number_of_transcribed_documents_string(self):
        number_of_transcribed_documents = functions.construct_number_of_transcribed_documents_string(self.project_one)
        self.assertEquals(number_of_transcribed_documents, '0/1')
        number_of_transcribed_documents = functions.construct_number_of_transcribed_documents_string(self.project_two)
        self.assertEquals(number_of_transcribed_documents, '1/1')

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)

