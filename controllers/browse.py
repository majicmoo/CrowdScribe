import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)
from gluon import *

def all():

    allprojects = general_module.attach_all_information_to_projects(database.get_open_projects())

    return dict(allprojects = allprojects)
