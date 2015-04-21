import unittest
import general_functions
import database_transactions
import projects_functions
import search_functions

db = test_db
database = database_transactions.DatabaseTransactions(db)
general_function = general_functions.GeneralFunctions(database, db)
project_function = projects_functions.ProjectFunctions(database, db)
search = search_functions.SearchFunctions(database, db)


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

        self.open_status = 'Open'
        self.tag_one = 'Sports'

        self.user_one = test_db.auth_user.insert(username="user_one")
        self.project_one = test_db.project.insert(name="project one", author_id=self.user_one, status=self.open_status,
                                                  description="description_one", tag=self.tag_one,
                                                  time_period_start_date=1900, time_period_end_date=2000)

    def test_empty_date_field(self):
        date = search.empty_field("")
        self.assertTrue(date)
        date = search.empty_field("test")
        self.assertFalse(date)

    def test_date_validator(self):

        eras = ['BC', 'AD']
        orders = ['Alphabetical', 'Earliest', 'Latest']

        advanced = FORM(
            INPUT(_name='advance', _id="advancetext"),
            LABEL("Category", SELECT(current.tags, _name='tag', requires=IS_IN_SET(current.tags))),
            LABEL("Start Date", INPUT(_name='start_date', _class='integer',
                                      requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 2016)))),
            SELECT(eras, _name='start_era', requires=IS_IN_SET(eras)),
            LABEL("End Date", INPUT(_name='end_date', _class='integer',
                                    requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 2016)))),
            SELECT(eras, _name='end_era', requires=IS_IN_SET(eras)),
            LABEL("Include Unknown dates?", INPUT(_name='include_unknown_date', _type='checkbox')),
            LABEL("Sort by", SELECT(orders, _name='order', requires=IS_IN_SET(orders))),
            INPUT(_value='Refine search', _type='submit', _id="advancesubmit"), _method='GET'
            )
        advanced.vars.start_date = "2025"
        advanced.vars.start_era = eras[0]
        advanced.vars.end_date = "2025"
        advanced.vars.end_era = eras[1]

        search.date_validator(advanced)
        self.assertEquals(advanced.errors.end_date, 'End date must be before 2015 AD')
        self.assertEquals(advanced.errors.start_date, 'Start date must be after 2015 BC')

        advanced.vars.start_date = "2005"
        advanced.vars.start_era = eras[1]
        advanced.vars.end_date = "2004"
        advanced.vars.end_era = eras[1]
        search.date_validator(advanced)
        self.assertEquals(advanced.errors.end_date, 'The End Date of the time period must be later than the Start Date')

    def test_search_project_for_keywords(self):
        result = search.search_project_for_keywords(["project"], self.project_one)
        self.assertFalse(result)
        result = search.search_project_for_keywords(["none"], self.project_one)
        self.assertTrue(result)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)
