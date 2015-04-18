import unittest
import database_transactions
db = test_db
database = database_transactions.DatabaseTransactions(db)




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

        # Setup arrays
        self.users = []
        self.projects = []
        self.documents = []
        self.fields = []
        self.transcriptions = []
        self.transcription_fields = []
        self.tags = []
        self.keywords = []

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
        self.tag_one = self.add_tag('Sports')
        self.tag_two = self.add_tag('Literature')

        # Setup keywords
        self.keyword = self.add_keyword('test')

        # Create User
        self.user_one = self.add_user('test1')
        self.user_two = self.add_user('test2')

        # Create Project
        self.project_one = self.add_project(name='testproject1', author_id=self.user_one,
                                                      status=self.open_status, description='test', tag=self.tag_one)
        self.project_two = self.add_project(name='testproject2', author_id=self.user_two,
                                                        status=self.closed_status, description='test', tag=self.tag_one)
        self.project_three = self.add_project(name='project1', author_id=self.user_one, status=self.open_status,
                                                      description='test', tag=self.tag_two)
        self.project_four = self.add_project(name='testproject4', author_id=self.user_one, status=self.open_status,
                                                      description='nothing', tag=self.tag_two)
        self.project_five = self.add_project(name='testproject5', author_id=self.user_one, status=self.under_review_status,
                                                      description='nothing', tag=self.tag_two)
        # Create Document Image
        self.document_one = self.add_document(description='test', project_id=self.project_one, status=self.open_status)
        self.document_two = self.add_document(description='test', project_id=self.project_one, status=self.closed_status)
        self.document_three = self.add_document(description='test', project_id=self.project_one, status=self.done_status)
        # Create Data Field
        self.data_field_one = self.add_field(project_id=self.project_one, name='test', short_description='test')
        # Create transcription
        self.transcription_one = self.add_transcription(document_id=self.document_one, author_id=self.user_two,
                                                        status=self.pending_status)
        self.transcription_two =  self.add_transcription(document_id=self.document_one, author_id=self.user_two,
                                                         status=self.accepted_status)
        self.transcription_three =  self.add_transcription(document_id=self.document_one, author_id=self.user_two,
                                                         status=self.rejected_status)
        # Create transcription field
        self.transcription_field_one = self.add_transcription_field(data_field_id=self.data_field_one,
                                                                    transcription_id=self.transcription_one,
                                                                    information='test')
        test_db.commit()

    def test_get_user(self):
        number_of_users = 0
        for user in self.users:
            # Check user object is returned
            test_user = database.get_user(user.id)
            self.assertEquals(test_user, user)
            number_of_users += 1
        # Check correct number of users are returned
        self.assertEquals(number_of_users, len(self.users))

    def test_get_project(self):
        number_of_projects = 0
        for project in self.projects:
            temp_project = database.get_project(project)
            self.assertEquals(temp_project, project)
            number_of_projects += 1
        self.assertEquals(number_of_projects, len(self.projects))

    def test_get_open_project(self):
        # Get Project 1: Should return Project
        project_one = database.get_open_project(self.project_one.id)
        self.assertEquals(project_one, self.project_one)
        self.assertEquals(project_one.status, self.open_status)

        # Get Project 2: Shouldn't return Project
        project_two = database.get_open_project(self.project_two.id)
        self.assertEquals(project_two, None)

    def test_get_all_projects(self):
        # Check correct number of projects are returned
        all_projects = len(database.get_all_projects())
        self.assertEquals(len(self.projects), all_projects)

    def test_get_open_projects(self):
        # Should Return 3 Open Projects
        projects = database.get_open_projects()
        self.assertEquals(len(projects), 3)
        for project in projects:
            self.assertEquals(project.status, self.open_status)

    def test_get_projects_for_user(self):
        projects_counted = 0
        for user in self.users:
            user_projects = database.get_projects_for_user(user)
            for i in user_projects:
                # Check all projects returned have correct username
                self.assertEquals(i.author_id.username, user.username)
                projects_counted += 1
        # Check all projects are found as all projects must be owned by a user
        self.assertEquals(projects_counted, len(self.projects))

    def test_get_open_projects_for_user(self):
        open_projects_counted_for_user = 0
        open_projects_counted = 0
        for user in self.users:
            user_projects = database.get_open_projects_for_user(user)
            for i in user_projects:
                # Check all projects returned have correct username
                self.assertEquals(i.author_id.username, user.username)
                self.assertEquals(i.status, self.open_status)
                open_projects_counted_for_user += 1

        for i in self.projects:
            if i.status == self.open_status:
                open_projects_counted += 1

        # Check all open  projects are found
        self.assertEquals(open_projects_counted_for_user, open_projects_counted)

    def test_get_open_projects_with_transcriptions_for_user(self):
        # Should Return only project 1
        open_projects_with_transcriptions_for_user = database.get_open_projects_with_transcriptions_for_user(self.user_one)
        self.assertEquals(len(open_projects_with_transcriptions_for_user),1)

        for project in open_projects_with_transcriptions_for_user:
            self.assertEquals(project.status, self.open_status)

        # Should Return No Projects
        open_projects_with_transcriptions_for_user = database.get_open_projects_with_transcriptions_for_user(self.user_two)
        self.assertEquals(len(open_projects_with_transcriptions_for_user),0)

    def test_get_open_projects_without_transcriptions_for_user(self):
        # Should Return No Projects
        open_projects_without_transcriptions_for_user = database.get_open_projects_without_transcriptions_for_user(self.user_two)
        self.assertEquals(len(open_projects_without_transcriptions_for_user),0)

        # Should Return Two Projects
        open_projects_without_transcriptions_for_user = database.get_open_projects_without_transcriptions_for_user(self.user_one)
        self.assertEquals(len(open_projects_without_transcriptions_for_user),2)
        for project in open_projects_without_transcriptions_for_user:
            self.assertEquals(project.status, self.open_status)

    def test_get_under_review_projects_for_user(self):
        under_review_projects = database.get_under_review_projects_for_user(self.user_one)
        # Should Return One Project
        self.assertEquals(len(under_review_projects),1)
        for i in under_review_projects:
            self.assertEquals(i.status, self.under_review_status)
            self.assertEquals(i.author_id, self.user_one)

    def test_get_closed_projects_for_user(self):
        closed_projects_counted_for_user = 0
        closed_projects_counted = 0
        for user in self.users:
            user_projects = database.get_closed_projects_for_user(user)
            for i in user_projects:
                # Check all projects returned have correct username
                self.assertEquals(i.author_id.username, user.username)
                self.assertEquals(i.status, self.closed_status)
                closed_projects_counted_for_user += 1

        for i in self.projects:
            if i.status == self.closed_status:
                closed_projects_counted += 1

        # Check all open  projects are found
        self.assertEquals(closed_projects_counted_for_user, closed_projects_counted)

    def test_get_projects_for_tag(self):
        projects = database.get_projects_for_tag(self.tag_one)
        self.assertEquals(len(projects), 1)
        projects = database.get_projects_for_tag(self.tag_two)
        self.assertEquals(len(projects), 2)


    def test_get_projects_for_keyword(self):
        total_number_of_open_projects_found_by_a = 0
        total_number_of_open_projects_found_by_b = 0
        # A
        for keyword in self.keywords:
            projects = database.get_projects_for_keyword(keyword)
            for project in projects:
                self.assertEquals(project.status, self.open_status)
                total_number_of_open_projects_found_by_a += 1
                if self.keyword in project.description:
                    self.assertIn(keyword, project.description)
                else:
                    self.assertIn(keyword, project.name)
        # B
        for i in self.projects:
            if i.status == self.open_status:
                total_number_of_open_projects_found_by_b += 1
        self.assertEquals(total_number_of_open_projects_found_by_a, total_number_of_open_projects_found_by_b)


    def test_get_random_open_project(self):
        project = database.get_random_open_project()
        is_project = True
        try:
            project.status
            project.time_period_start_date
            project.description
            project.tag
            project.time_period_end_date
            project.author_id
            project.name
        except NameError:
            is_project = False
        self.assertTrue(is_project)

    def test_get_number_of_transcribed_documents_for_project(self):
        # 2 transcriptions for document on project 1
        number_of_transcribed_documents = database.get_number_of_transcribed_documents_for_project(self.project_one)
        self.assertEquals(1, number_of_transcribed_documents)

        # Project 3 has no transcriptions
        number_of_transcribed_documents = database.get_number_of_transcribed_documents_for_project(self.project_three)
        self.assertEquals(0, number_of_transcribed_documents)


    def test_get_document(self):
        number_of_documents = 0
        for document in self.documents:
            temp_document =database.get_document(document)
            self.assertEquals(temp_document, document)
            number_of_documents += 1
        self.assertEquals(number_of_documents, len(self.documents))

    def test_get_documents_for_project(self):
        total_number_of_documents = 0
        for project in self.projects:
            project_documents = database.get_documents_for_project(project)
            for document in project_documents:
                total_number_of_documents += 1
                self.assertEquals(document.project_id, project.id)
        self.assertEquals(total_number_of_documents, len(self.documents))

    def test_get_open_documents_for_project(self):
        total_number_of_open_documents_found_by_a = 0
        total_number_of_open_documents_found_by_b = 0
        # A
        for project in self.projects:
            project_documents = database.get_open_documents_for_project(project)
            for document in project_documents:
                total_number_of_open_documents_found_by_a += 1
                self.assertEquals(document.project_id, project.id)
                self.assertEquals(document.status, self.open_status)
        # B
        for i in self.documents:
            if i.status == self.open_status:
                total_number_of_open_documents_found_by_b += 1

        self.assertEquals(total_number_of_open_documents_found_by_a, total_number_of_open_documents_found_by_b)

    def test_get_open_documents_with_transcription_for_project(self):
        open_documents_with_transcription = database.get_open_documents_with_transcription_for_project(self.project_one)
        # Should Return 1 document
        self.assertEquals(len(open_documents_with_transcription),1)
        for i in open_documents_with_transcription:
            self.assertEquals(i.status, self.open_status)
            self.assertEquals(i.project_id, self.project_one.id)

        open_documents_with_transcription = database.get_open_documents_with_transcription_for_project(self.project_two)
        # Should Return 0 documents
        self.assertEquals(len(open_documents_with_transcription),0)

    def test_get_open_documents_without_transcription_for_project(self):
        open_documents_without_transcription = database.get_open_documents_without_transcription_for_project(self.project_one)
        # Should Return 0 documents
        self.assertEquals(len(open_documents_without_transcription),0)

        open_documents_without_transcription = database.get_open_documents_without_transcription_for_project(self.project_two)
        # Should Return 0 documents
        self.assertEquals(len(open_documents_without_transcription),0)

    def test_get_closed_documents_for_project(self):
        total_number_of_closed_documents_found_by_a = 0
        total_number_of_closed_documents_found_by_b = 0
        # A
        for project in self.projects:
            project_documents = database.get_closed_documents_for_project(project)
            for document in project_documents:
                total_number_of_closed_documents_found_by_a += 1
                self.assertEquals(document.project_id, project.id)
                self.assertEquals(document.status, self.closed_status)
        # B
        for i in self.documents:
            if i.status == self.open_status:
                total_number_of_closed_documents_found_by_b += 1

        self.assertEquals(total_number_of_closed_documents_found_by_a, total_number_of_closed_documents_found_by_b)

    def test_get_done_documents_for_user(self):
        total_number_of_done_documents_found_by_a = 0
        total_number_of_done_documents_found_by_b = 0
        # A
        for user in self.users:
            documents = database.get_done_documents_for_user(user)
            for document in documents:
                total_number_of_done_documents_found_by_a += 1
                self.assertEquals(document.document_image.status, self.done_status)
                self.assertEquals(document.project.author_id, user)
        # B
        for document in self.documents:
            if document.status == self.done_status:
                total_number_of_done_documents_found_by_b += 1
        self.assertEquals(total_number_of_done_documents_found_by_a, total_number_of_done_documents_found_by_b)

    def test_get_done_documents_for_project(self):
        total_number_of_done_documents_found_by_a = 0
        total_number_of_done_documents_found_by_b = 0
        # A
        for project in self.projects:
            documents = database.get_done_documents_for_project(project)
            for document in documents:
                total_number_of_done_documents_found_by_a += 1
                self.assertEquals(document.status, self.done_status)
                self.assertEquals(document.project_id, project)
        # B
        for document in self.documents:
            if document.status == self.done_status:
                total_number_of_done_documents_found_by_b += 1
        self.assertEquals(total_number_of_done_documents_found_by_a, total_number_of_done_documents_found_by_b)

    def test_get_documents_with_transcription_for_project(self):
        documents_with_transcription = database.get_documents_with_transcription_for_project(self.project_one.id)
        self.assertEquals(len(documents_with_transcription), 1)

        documents_with_transcription_2 = database.get_documents_with_transcription_for_project(self.project_two.id)
        self.assertEquals(len(documents_with_transcription_2), 0)

    def test_get_successfully_transcribed_documents_for_project(self):
        successfully_transcribed_documents = database.get_successfully_transcribed_documents_for_project(self.project_one)
        # Should return 1 document
        self.assertEquals(len(successfully_transcribed_documents),1)

        successfully_transcribed_documents = database.get_successfully_transcribed_documents_for_project(self.project_two)
        # Should return 0 documents
        self.assertEquals(len(successfully_transcribed_documents),0)

    def test_get_documents_with_transcription_for_user(self):
        # Documents user own and have a transcription
        documents = database.get_documents_with_transcription_for_user(self.user_one)
        self.assertEquals(len(documents), 1)

        documents = database.get_documents_with_transcription_for_user(self.user_two)
        self.assertEquals(len(documents), 0)

    def test_document_has_already_been_transcribed_by_user(self):
        transcribed = database.document_has_already_been_transcribed_by_user(self.document_one, self.user_two)
        self.assertTrue(transcribed)

        transcribed = database.document_has_already_been_transcribed_by_user(self.document_two, self.user_two)
        self.assertFalse(transcribed)

    #FIXME: ...
    def test_document_transcribed_by_user(self):
        pass

    def test_get_documents_with_transcription_for_project_and_transcription_author(self):
        documents = database.get_documents_with_transcription_for_project_and_transcription_author(self.project_one, self.user_two)
        self.assertEquals(len(documents), 1)

        documents = database.get_documents_with_transcription_for_project_and_transcription_author(self.project_two, self.user_two)
        self.assertEquals(len(documents), 0)

        documents = database.get_documents_with_transcription_for_project_and_transcription_author(self.project_two, self.user_one)
        self.assertEquals(len(documents), 0)

    def test_get_document_for_project_header(self):
        document = database.get_document_for_project_header(self.project_one)
        self.assertEquals(document,self.document_one)

        document = database.get_document_for_project_header(self.project_two)
        self.assertEquals(document, None)

    def test_get_documents_with_no_transcriptions_for_project(self):
        documents = database.get_documents_with_no_transcriptions_for_project(self.project_one)
        self.assertEquals(len(documents), 2)

        documents = database.get_documents_with_no_transcriptions_for_project(self.project_two)
        self.assertEquals(len(documents), 0)

    def test_get_document_for_transcription(self):
        document = database.get_document_for_transcription(self.transcription_one)
        self.assertEquals(document, self.document_one)
        document = database.get_document_for_transcription(self.transcription_two)
        self.assertEquals(document, self.document_one)

    def test_get_pending_transcriptions_for_user(self):
        transcriptions = database.get_pending_transcriptions_for_user(self.user_one)
        self.assertEquals(len(transcriptions), 0)
        transcriptions = database.get_pending_transcriptions_for_user(self.user_two)
        self.assertEquals(len(transcriptions), 1)

    def test_get_accepted_transcriptions_for_user(self):
        transcriptions = database.get_accepted_transcriptions_for_user(self.user_one)
        self.assertEquals(len(transcriptions), 0)
        transcriptions = database.get_accepted_transcriptions_for_user(self.user_two)
        self.assertEquals(len(transcriptions), 1)

    def test_get_rejected_transcriptions_for_user(self):
        transcriptions = database.get_rejected_transcriptions_for_user(self.user_one)
        self.assertEquals(len(transcriptions), 0)
        transcriptions = database.get_rejected_transcriptions_for_user(self.user_two)
        self.assertEquals(len(transcriptions), 1)

    def test_get_transcription(self):
        for transcription in self.transcriptions:
            temp = database.get_transcription(transcription.id)
            self.assertEquals(temp, transcription)

    def test_get_transcriptions_for_document(self):
        transcriptions = database.get_transcriptions_for_document(self.document_one)
        self.assertEquals(len(transcriptions), 3)
        transcriptions = database.get_transcriptions_for_document(self.document_two)
        self.assertEquals(len(transcriptions), 0)

    def test_get_pending_transcriptions_for_document(self):
        transcriptions = database.get_pending_transcriptions_for_document(self.document_one)
        self.assertEquals(len(transcriptions), 1)
        transcriptions = database.get_pending_transcriptions_for_document(self.document_two)
        self.assertEquals(len(transcriptions), 0)

    def test_get_accepted_transcription_for_document(self):
        transcription = database.get_accepted_transcription_for_document(self.document_one)
        self.assertEquals(transcription, self.transcription_two)
        transcription = database.get_accepted_transcription_for_document(self.document_two)
        self.assertEquals(transcription, None)

    def test_get_data_fields_for_project(self):
        total_number_of_data_fields = 0
        for project in self.projects:
            data_fields = database.get_data_fields_for_project(project)
            for data_field in data_fields:
                total_number_of_data_fields += 1
                self.assertEquals(data_field.project_id, self.project_one)
        self.assertEquals(total_number_of_data_fields, len(self.fields))

    def test_get_transcribed_fields_for_transcription(self):
        total_number_of_transcribed_fields = 0
        for transcription in self.transcriptions:
            transcribed_fields = database.get_transcribed_fields_for_transcription(transcription)
            for transcribed_field in transcribed_fields:
                # Check right transcription ID
                self.assertEquals(transcribed_field.transcribed_field.transcription_id, transcription)
                total_number_of_transcribed_fields += 1
        self.assertEquals(len(self.transcription_fields), total_number_of_transcribed_fields)

    def test_project_can_be_closed_for_review(self):
        close_project = database.project_can_be_closed_for_review(self.project_one)
        self.assertTrue(close_project)
        close_project = database.project_can_be_closed_for_review(self.project_two)
        self.assertFalse(close_project)






    # FIXME
    def test_get_transcriptions_by_user(self):
        pass
        # total_number_of_transcriptions = 0
        # for user in self.users:
        #     transcriptions = database.get_transcriptions_by_user(user)
        #     for transcription in transcriptions:
        #         total_number_of_transcriptions += 1
        #         self.assertEquals(transcription.author_id, user)
        #
        # self.assertEquals(total_number_of_transcriptions, len(self.transcriptions))













    def test_get_documents_for_a_project_that_have_transcription(self):
        # FIXME: Not sure if the database transaction works for this one
        pass
        # documents = database.get_documents_for_a_project_that_have_transcription(self.project_open_id)
        # for i in documents:
        #     print i
        #     self.assertEquals(i.document_image.project_id, self.project_open_id)
        #     self.assertTrue(self.exists(i.transcription.id))




##########################
    def add_user(self, username):
        user = test_db.auth_user.insert(username=username)
        self.users.append(user)
        return user

    def add_project(self, name, author_id,status, description, tag):
        project = test_db.project.insert(name=name, author_id=author_id, status=status, description=description,
                                         tag=tag)
        self.projects.append(project)
        return project

    def add_document(self, description, project_id, status):
        document = test_db.document_image.insert(description=description,project_id=project_id, status=status)
        self.documents.append(document)
        return  document


    def add_field(self, project_id, name, short_description):
        field = test_db.data_field.insert(project_id=project_id, name=name, short_description=short_description)
        self.fields.append(field)
        return field

    def add_transcription(self, document_id, author_id, status):
        transcription = test_db.transcription.insert(document_id=document_id, author_id=author_id, status=status)
        self.transcriptions.append(transcription)
        return transcription

    def add_transcription_field(self, data_field_id, transcription_id, information):
        field = test_db.transcribed_field.insert(data_field_id=data_field_id, transcription_id=transcription_id,
                                                 information=information)
        self.transcription_fields.append(field)
        return field

    def add_tag(self, tag):
        self.tags.append(tag)
        return tag

    def add_keyword(self, keyword):
        self.keywords.append(keyword)
        return keyword


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)
