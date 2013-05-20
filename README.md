salim
=====

Salim is an API for development of personal finance software.
Salim is a Python software and uses [Storm ORM](https://storm.canonical.com/) to abstract the database interface, so we can use Postgress, MySQL or SQLite as database systems.
Salim intends to provide a structured way to store the financial information obtained from OFX and CSV files (we also consider to support OFC format).

#Salim Mushiba – Personal Finance Software

Salim Mushiba is a software for personal finance with focus on build the budget and check whether it will or will not be achieved during the period into analysis (usually one month).

The main challenges are:

* Build monthly budget
  * Extrapolate to an yearly basis, computing annual results per segment/category
  * Split the total yearly budget into a monthly basis, so I can have an average number per segment/category
  * Compare budgets. I can have more than one budget for a month because sometimes I want to test some cases
* Check if the budgeted targets are being achieved
* Give budget x real cash flow
* Answer the question: how much money do I have today?
* Import OFX (maybe OFC) files
* Link account information with budget information. It's relevant when I have 2 or more budgets related to the same period of time. It makes possible to compare the performance of distinct budgets.
* Create nice graphics.

Some technical specifications:

* Web 2.0 standards compliance
* implemented in Python using the web framework Django
* use SQLite as database backend

Tasks:


* import OFX (maybe OFC) files
  * an OFX file is mainly charactherized by its LedgerBalance information.
  * the LedgerBalance is related to its BankAccount
  * each StatementTransaction imported is related to a LegderBalance and as a consequence it is related to LedgerBalance's BankAccount
  * a StatementTransaction is constrainted to its date, amount and memo. I think that it must be constrainted to its fitid code, it seems to be unique.
  * check whether the new imported transactions match the last LedgerBalance imported.
* compute the balance for each day using the transactions and the last imported balance.
* summarize the daily balances to generate a final balance representing the complete financial situation.

ENB Metric

Expenses Not Budgeted = ENB
Expenses Not Budgeted Rate = r
r = ENB / days
r can be estimated throught the history.

Entities Classes

* BankAccount
* LedgerBalance
* StatementTransaction
  * pay date
  * due date
  * value
  * value paid
  * description/comment
* Account Registry
  * account name
	* category
	* value - use last value paid to account
	* day (date) - use last
	* frequency - monthy, 2 monthly, quartely, semiannual, annual ...
* PayEvent
	* id_registry
* Budget
	* transactions
	* year (reference)
	* month
	* description/identification
* TransactionModel (identifying transactions)
	* identification/name
	* type
	* day
	* amount
	* frequency
* Transaction
	* date
	* amount
	* description/comments
	* type (Income, Expense)
	* identification/name
