import unittest
import database_transactions as database

from gluon.globals import Request
db = test_db

#execfile("applications/api/controllers/10.py", globals())

#db.commit()

class TestDatabaseTransactions(unittest.TestCase):
    def setUp(self):
        #request = Request()  # Use a clean Request object
        pass

    def testListActiveGames(self):
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


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDatabaseTransactions))
unittest.TextTestRunner(verbosity=2).run(suite)

