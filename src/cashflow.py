#!/usr/bin/env python

from datetime import date
from salim.model import BankAccount, StatementTransaction, LedgerBalance
from storm.locals import Store, create_database, Desc

DATABASE = create_database( "sqlite:salim.db" )
STORE = Store( DATABASE )

date_beg = date(2008,6,1)
date_end = date(2008,6,30)

accounts = [ account for account in STORE.find( BankAccount ) if account.id == 2 ]
result = STORE.find( LedgerBalance )

balances = [ balance for balance in result.order_by( Desc(LedgerBalance.date) ) ]
balances = [ balance for balance in balances if balance.bank_account.account == u"05017883437" ]

cons = {}
stmt = {}
for account in accounts:
    transactions = STORE.find( StatementTransaction, StatementTransaction.bank_account == account,
        StatementTransaction.date >= date_beg )

    for trans in transactions:
        try:
            cons[trans.date] += trans.amount
        except KeyError, ex:
            cons[trans.date] = trans.amount
    keys = cons.keys()
    keys.sort()
    keys.reverse()

    result = STORE.find( LedgerBalance, LedgerBalance.bank_account == account )
    balances = [ balance for balance in result.order_by( Desc(LedgerBalance.date) ) ]

    balance = balances[0]
    amt = balance.amount
    for key in keys:
        if key in stmt:
            stmt[key] += amt
        else:
            stmt[key] = amt
        amt -= cons[key]

for key in keys:
    amt = stmt[key]
    print "%12s%10.2f" % (key, amt)
