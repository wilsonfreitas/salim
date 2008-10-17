#!/usr/bin/env python
# encoding: utf-8
"""
facade.py

Created by Wilson Freitas on 2008-09-12.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from salim.ofx import OFXFileParser
from salim.model import *
from salim import model
import logging


class OFXImport(object):
    def __init__(self, filename):
        ofx = OFXFileParser(filename)
        self.__import_data(ofx)
        logging.info('*')
        logging.info('* OFXImport report')
        logging.info('* Filename:             %s' % filename)
        logging.info('* Bank name:            %s' % self.bank_account.name)
        logging.info('* Bank account:         %s' % self.bank_account.account)
        logging.info('* Balance date:         %s' % (self.balance and str(self.balance.date)))
        logging.info('* Total transctions:    %d' % len(ofx['StmtTrn']))
        logging.info('* Transctions imported: %d' % (bool(self.balance) and self.balance.transactions.count()))
        logging.info('*')

    def __import_data(self, ofx):
        # -- saving bank account
        self.bank_account = model.store.get(BankAccount, ofx['acctid'])
        if not bool(self.bank_account):
            logging.debug('Saving bank account: %s' % ofx['acctid'])
            d = { 'bankid': int(ofx['bankid']), 'branch': ofx['branchid'], 'account': ofx['acctid'] }
            self.bank_account = model.store.add(BankAccount(**d))
        else:
            logging.debug('Found bank account: %s' % ofx['acctid'])
        
        # -- saving balance
        if not bool(LedgerBalance.by_bank_account_and_date(self.bank_account, str2date(ofx['ledgerbal']['dtasof']))):
            model.store.commit()
            d = { 'date': str2date(ofx['ledgerbal']['dtasof']), 'amount': float(ofx['ledgerbal']['balamt']),
                  'bank_account': self.bank_account }
            self.balance = LedgerBalance(**d)
            # -- saving statement transactions
            for _transaction in ofx['StmtTrn']:
                d = { 'date' : str2date(_transaction['dtposted']), 'amount' : float(_transaction['trnamt']),
                      'memo' : _transaction['memo'], 'checknum' : _transaction['checknum'],
                      'fitid' : _transaction['fitid'] }
                transaction = self.balance.add_transaction(StatementTransaction(**d))
                if transaction is not None:
                    logging.debug('Importing transaction: <DATE %s> <AMOUNT %.2f> <MEMO %s>' % (
                                  transaction.date, transaction.amount, transaction.memo) )
            model.store.commit()
            logging.debug('Commiting bank account %s at date %s' % (self.bank_account.account, str(self.balance.date)))
            # -- checking balance
#             if self.balance.is_valid():
#                 model.store.commit()
#                 logging.debug('Commiting balance at date %s' % str(self.balance.date))
#             else:
#                 logging.warn('Invalid balance at date %s' % str(self.balance.date))
#                 model.store.rollback()
#                 raise AssertionError('''Validation error: balance amount does not match transactions calculation:
#     Gap = %.4f
# ''' % self.balance._accum)
        else:
            self.balance = None

def import_ofx(filename):
    return OFXImport(filename)

def find_transactions_after_date(date, account):
    previous_balance = LedgerBalance.previous(date, account)
    balance_amount   = previous_balance.amount

    for balance in LedgerBalance.find_after(previous_balance):
        for stmt in StatementTransaction.by_balance(balance):
            if stmt.date >= date:
                yield (stmt, balance_amount)
            balance_amount += stmt.amount

def find_balance_amount_for_date(date, account):
    previous_balance = LedgerBalance.previous(date, account)
    balance_amount   = previous_balance.amount

    for balance in LedgerBalance.find_after(previous_balance):
        for stmt in StatementTransaction.by_balance(balance):
            if stmt.date >= date:
                return balance_amount
            balance_amount += stmt.amount

def find_budget_entries_after_date(date):
    return BudgetEntry.find_after_date(date)