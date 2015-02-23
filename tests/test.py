import unittest
import database_transactions as database

from gluon.globals import Request
#db = test_db

#execfile("applications/api/controllers/10.py", globals())

#db.commit()

class TestDatabaseTransactions(unittest.TestCase):
    def setUp(self):
        #request = Request()  # Use a clean Request object
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

        pass

    def get_user_test(self):
        # Set variables for the test function
        # request.post_vars["game_id"] = 1
        # request.post_vars["username"] = "spiffytech"
        # bob = request.post_vars["game_id"]
        print "Here"
        test = database.get_user(db,1)
        print "2ndHere"
        #resp = list_active_games()
        db.commit()
        self.assertEquals(1, len(test))

    def get_all_projects_test(self):
        #database.get_all_projects(db)
        pass

    def get_projects_by_user_test(self):
        #database.get_project_by_user(db, user_id)
        pass


    def get_open_projects_by_user_test(self):
        #database.get_open_projects_by_user(db, user_id)
        pass


    def get_closed_projects_by_user_test(self):
        #database.get_closed_projects_by_user(db, user_id)
        pass


    def get_project_documents_test(self):
        #database.get_project_documents(db, user_id)
        pass


    def get_project_open_documents_test(self):
        # database.get_project_open_documents(db, project_id)
        pass


    def get_project_closed_documents_test(self):
        #database.get_project_closed_documents(db, project_id)
        pass


    def get_projects_by_tag(self):
        #database.get_projects_by_tag(db, tag)
        pass


    def get_projects_by_keyword_test(self):
        #database.get_projects_by_keyword(db, keyword)
        pass


    def get_transcriptions_by_user_test(self):
        #database.get_transcriptions_by_user(db, user_id)
        pass


    def get_transcribed_fields_for_transcription(self):
        #database.get_transcribed_fields_for_transcription(db, transcription_id)
        pass


    def get_data_fields_for_project(self):
        #database.get_data_fields_for_project(db, project_id)
        pass


    def get_transcriptions_for_document(self):
        #database.get_transcriptions_for_document(db, document_id)
        pass


    def get_done_documents_for_user(self):
        #database.get_done_documents_for_user(db, user_id)
        pass


    def get_done_documents_for_project_test(self):
        #database.get_done_documents_for_project(db, project_id)
        pass


    def get_documents_for_a_user_that_have_transcription_test(self):
        #database.get_documents_for_a_user_that_have_transcription(db, user_id)
        pass


    def get_documents_for_a_project_that_have_transcription_test(self):
        #database.get_documents_for_a_project_that_have_transcription(db, project_id)
        pass



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)

