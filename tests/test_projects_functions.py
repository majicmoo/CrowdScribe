import unittest
import general_functions
import database_transactions
import projects_functions
db = test_db
database = database_transactions.DatabaseTransactions(db)
general_function = general_functions.GeneralFunctions(database, db)
functions = projects_functions.ProjectFunctions(database, db)


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
        self.user_two = test_db.auth_user.insert(username="user_two")

        # Projects
        self.project_one = test_db.project.insert(name="project_one", author_id=self.user_one, status=self.open_status,
                                                  description="description_one", tag=self.tag_one,
                                                  time_period_start_date=1900, time_period_end_date=2000)
        self.project_two = test_db.project.insert(name="project_two", author_id=self.user_one, status=self.open_status,
                                                  description="description_two", tag=self.tag_one,
                                                  time_period_start_date=1800, time_period_end_date=1850)
        self.projects = [self.project_one, self.project_two]

        # Documents
        self.document_one = test_db.document_image.insert(description="description_one", image="temp",
                                                          project_id=self.project_one, status=self.open_status)
        self.document_two = test_db.document_image.insert(description="description_two", image="temp",
                                                          project_id=self.project_one, status=self.closed_status)
        self.documents = [self.document_one, self.document_two]

        self.data_field_one = test_db.data_field.insert(project_id=self.project_one, name="name one",
                                                        short_description="short description")

        self.transcription_one = test_db.transcription.insert(document_id=self.document_one, author_id=self.user_two,
                                                              status=self.pending_status)

        self.transcribed_field_one = test_db.transcribed_field.insert(data_field_id=self.data_field_one,
                                                                      transcription_id=self.transcription_one,
                                                                      information="information")

    def test_check_if_steps_available(self):
        steps_available = functions.check_if_steps_available(self.project_one)
        steps_available[2] = True
        steps_available[3] = True
        steps_available[4] = False

        steps_available = functions.check_if_steps_available(self.project_two)
        steps_available[2] = True
        steps_available[3] = False
        steps_available[4] = False

    def test_retrieve_prepopulated_data_for_create_step_1(self):
        data = functions.retrieve_prepopulated_data_for_create_step_1(self.project_one)
        self.assertEquals(data['name'], self.project_one.name)
        self.assertEquals(data['description'], self.project_one.description)
        self.assertEquals(data['start_date'], self.project_one.time_period_start_date)
        self.assertEquals(data['end_date'], self.project_one.time_period_end_date)

    def test_validate_create_step1(self):
        # These were manually tested
        pass

    def test_validate_add_image_form(self):
        # These were manually tested
        pass

    def test_validate_add_field_form(self):
        # These were manually tested
        pass

    def test_attach_number_of_transcriptions(self):
        functions.attach_number_of_transcriptions(self.documents)
        self.assertEquals(self.documents[0].number_of_transcriptions, 1)
        self.assertEquals(self.documents[1].number_of_transcriptions, 0)

    def test_attach_number_of_transcriptions_to_lists_of_documents(self):
        document_a = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.closed_status)
        document_b = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.closed_status)
        document_c = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.closed_status)
        document_d = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.closed_status)
        list_of_lists = [[self.document_one, self.document_two], [document_b, document_c], [document_a, document_d]]
        functions.attach_number_of_transcriptions_to_lists_of_documents(list_of_lists)
        self.assertEquals(list_of_lists[0][0].number_of_transcriptions, 1)
        self.assertEquals(list_of_lists[0][1].number_of_transcriptions, 0)
        self.assertEquals(list_of_lists[1][0].number_of_transcriptions, 0)
        self.assertEquals(list_of_lists[1][1].number_of_transcriptions, 0)
        self.assertEquals(list_of_lists[2][0].number_of_transcriptions, 0)
        self.assertEquals(list_of_lists[2][1].number_of_transcriptions, 0)

    def test_if_none_convert_to_empty_list(self):
        test = functions.if_none_convert_to_empty_list(None)
        self.assertEquals(test, [])
        test = functions.if_none_convert_to_empty_list("test")
        self.assertEquals(test, "test")

    def test_set_up_project_page_based_on_user(self):
        document_a = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.open_status)
        document_b = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.open_status)
        document_c = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.done_status)
        document_d = test_db.document_image.insert(description="description_two", image="temp",
                                                   project_id=self.project_one, status=self.closed_status)
        auth.user = self.user_one
        (open_documents, open_documents_with_transcription, open_documents_without_transcription, done_documents,
         closed_documents) = functions.set_up_project_page_based_on_user(self.project_one, auth)

        self.assertEquals(len(open_documents), 0)
        self.assertEquals(open_documents_with_transcription[0], self.document_one)
        self.assertEquals(open_documents_without_transcription[0], document_a)
        self.assertEquals(open_documents_without_transcription[1], document_b)
        self.assertEquals(done_documents[0], document_c)
        self.assertEquals(closed_documents[0], self.document_two)
        self.assertEquals(closed_documents[1], document_d)

        auth.user = self.user_two
        (open_documents, open_documents_with_transcription, open_documents_without_transcription, done_documents,
         closed_documents) = functions.set_up_project_page_based_on_user(self.project_one, auth)
        self.assertEquals(open_documents[0], self.document_one)
        self.assertEquals(open_documents[1], document_a)
        self.assertEquals(open_documents[2], document_b)
        self.assertEquals(len(open_documents_with_transcription), 0)
        self.assertEquals(len(open_documents_without_transcription), 0)
        self.assertEquals(done_documents[0], document_c)
        self.assertEquals(len(closed_documents), 0)

    def test_check_if_step1_was_skipped_and_redirect_if_so(self):
        session.project_being_created = self.project_two
        project_id, project_being_edited = functions.check_if_step1_was_skipped_and_redirect_if_so(session)
        self.assertEquals(project_id, self.project_two)
        self.assertEquals(project_being_edited, self.project_two)

    def test_check_if_come_back_from_future_step(self):
        session.project_being_created = self.project_two
        project_id, project_being_edited = functions.check_if_come_back_from_future_step(session)
        self.assertEquals(project_id, self.project_two)
        self.assertEquals(project_being_edited, self.project_two)

    def test_create_clear_project_form(self):
        # These were manually tested
        pass

    def test_create_next_step_form(self):
        # These were manually tested
        pass

    def test_create_previous_step_form(self):
        # These were manually tested
        pass

    def test_process_start_and_end_dates(self):
        current.request.vars.time_period_start_date = '1900'
        current.request.vars.time_period_end_date = '2000'
        current.request.vars.start_era = "AD"
        current.request.vars.end_era = "AD"
        start_date, end_date = functions.process_start_and_end_dates()
        self.assertEquals(start_date, 1900)
        self.assertEquals(end_date, 2000)

        current.request.vars.time_period_start_date = '1900'
        current.request.vars.time_period_end_date = '2000'
        current.request.vars.start_era = "BC"
        current.request.vars.end_era = "BC"
        start_date, end_date = functions.process_start_and_end_dates()
        self.assertEquals(start_date, -1900)
        self.assertEquals(end_date, -2000)

    def test_build_transcription_list(self):
        # These were manually tested
        pass

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)
