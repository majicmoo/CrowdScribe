import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)

def debug():
	response.title = "Debug";
	return dict();