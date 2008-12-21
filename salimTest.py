#!/usr/bin/python
# -*- encoding: latin1 -*-

import sys
sys.path.append('./src')

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
from salim.ofx import OFXFileParser, OFXTextParser
from salim.model import *
# from salim.csvadapter import *
from datetime import date


class TestOFXParser(TestCase):
    ofx_text = '''
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
<OFX>
<BANKMSGSRSV1>
  <STMTTRNRS>
     <STMTRS>
        <BANKACCTFROM>
           <BANKID>1</BANKID>
           <BRANCHID>3520-3</BRANCHID>
           <ACCTID>14329-4</ACCTID>
           <ACCTTYPE>CHECKING</ACCTTYPE>
        </BANKACCTFROM>
        <BANKTRANLIST>
           <DTSTART>20080430120000[-3:BRT]</DTSTART>
           <DTEND>20080528120000[-3:BRT]</DTEND>
           <STMTTRN>
              <TRNTYPE>OTHER</TRNTYPE>
              <DTPOSTED>20080505120000[-3:BRT]</DTPOSTED>
              <TRNAMT>-60.95</TRNAMT>
              <FITID>20080505160950</FITID>
              <CHECKNUM>000000153704</CHECKNUM>
              <REFNUM>153.704</REFNUM>
              <MEMO>Compra com Cartão - 03/05 14:55 CARREFOUR 2 RJB -</MEMO>
           </STMTTRN>
           <STMTTRN>
              <TRNTYPE>OTHER</TRNTYPE>
              <DTPOSTED>20080505120000[-3:BRT]</DTPOSTED>
              <TRNAMT>-74.50</TRNAMT>
              <FITID>20080505174500</FITID>
              <CHECKNUM>000000256395</CHECKNUM>
              <REFNUM>256.395</REFNUM>
              <MEMO>Compra com Cartão - 03/05 15:39 LEROY MERLIN</MEMO>
           </STMTTRN>
         </BANKTRANLIST>
     </STMTRS>
  </STMTTRNRS>
</BANKMSGSRSV1>
</OFX>
'''

    def setUp(self):
        self.parser = OFXTextParser(self.ofx_text)
    
    def tearDown(self):
        pass
    
    def test_fetch(self):
        '''testing case insensitive keys'''
        self.assertEqual(self.parser['BANKID'], '1')
        self.assertEqual(self.parser['BRANCHID'], '3520-3')
        self.assertEqual(self.parser['ACCTID'], '14329-4')
        # TODO: Correct this!
        # bank_info = parser['BANKACCTFROM']
        # self.assertEqual(bank_info['BANKID'], '1')
        # self.assertEqual(bank_info['BRANCHID'], '3520-3')
        # self.assertEqual(bank_info['ACCTID'], '14329-4')
    
    def test_bank_info(self):
        '''testing retrieval of bank info from dict structure'''
        bank_info = self.parser['bankacctfrom']
        self.assertEqual(bank_info['bankid'], '1')
        self.assertEqual(bank_info['branchid'], '3520-3')
        self.assertEqual(bank_info['acctid'], '14329-4')
    
    def test_bank_info2(self):
        '''testing retrieval of bank info from OFXParser structure'''
        self.assertEqual(self.parser['bankid'], '1')
        self.assertEqual(self.parser['branchid'], '3520-3')
        self.assertEqual(self.parser['acctid'], '14329-4')
    
    def test_statements(self):
        '''testing statements retrieval'''
        stmt = self.parser['StmtTrn']
        self.assertEqual(len(stmt), 2)
        self.assertEqual(stmt[0]['trnamt'], '-60.95')
        self.assertEqual(stmt[0]['memo'], 'Compra com Cartão - 03/05 14:55 CARREFOUR 2 RJB -')
        self.assertEqual(stmt[1]['fitid'], '20080505174500')
    

class TestOFXFileParser(TestCase):

    def setUp(self):
        self.parser = OFXFileParser("tests/Test4.ofx")
    
    def test_print_unicode(self):
        '''testing printing unicode statements'''
        # str.decode()
        # str --> | decode | --> unicode
        # str.encode()
        # unicode --> | encode | --> str
        stmt = self.parser['StmtTrn']
        def print_():
            print 'test', stmt[0]['memo']
        self.assertRaises(UnicodeEncodeError, print_)
        print 'test', stmt[0]['memo'].encode('utf-8')
    

class TestDB(TestCase):
    '''Test salim database'''

    def setUp(self):
        """docstring for setUp"""
        self.store = create_database('sqlite:')
        read_file(self.store, './src/salim.sql')
        self.parser = OFXFileParser( "./tests/Test4.ofx")
        self.parser1 = OFXFileParser("./tests/Test1.ofx")
        self.parser2 = OFXFileParser("./tests/Test2.ofx")
    
    def tearDown(self):
        """docstring for tearDown"""
        destroy_database()
    
    def _get_statement(self, info, balance, category):
        d = {
        'date' : str2date(info['dtposted']),
        'amount' : float(info['trnamt']),
        'memo' : info['memo'],
        'checknum' : info['checknum'],
        'fitid' : info['fitid'],
        'balance' : balance,
        'category' : category
        }

        tr = StatementTransaction(**d)
        self.store.add(tr)
        self.store.commit()
        return tr
    
    def _get_bank_account(self, ofx):
        bank_acc = BankAccount()
        bank_acc.bankid = int(ofx['bankid'])
        bank_acc.account = ofx['acctid']
        bank_acc.branch = ofx['branchid']
        self.store.add(bank_acc)
        self.store.commit()
        return bank_acc
    
    def _get_balance(self, info, bankacc):
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': bankacc
        }
        bal = LedgerBalance(**d)
        self.store.add(bal)
        self.store.commit()
        return bal
    

class TestCategory(TestDB):
    """Test Category in salim database"""
        
    def test_category_insertion(self):
        """testing Category insertion"""
        # testing Category insert
        cat1 = Category(u'Casa')
        self.store.add(cat1)
        self.assertEqual(cat1.name, u'Casa')
        # self.assertEqual(self.store.find(Category).count(), 1)

    def test_category_find(self):
        """testing Category insertion and retrieval"""
        cat1 = Category(u'Casa')
        self.store.add(cat1)
        cat2 = self.store.get(Category, u'Casa')
        self.assertEqual(cat1.name, cat2.name)

    def test_category_double_insertion(self):
        """testing Category insertion with the same name: IntegrityError on commit"""
        self.store.add(Category(u'Casa'))
        self.store.add(Category(u'Casa'))
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, self.store.commit)
    
    def test_category_update(self):
        """testing Category name updating for an existing name: IntegrityError on commit"""
        self.store.add(Category(u'Casa'))
        self.store.add(Category(u'Cartões'))
        self.store.commit()
        def update():
            self.store.find(Category, Category.name == u'Casa').set(name=u'Cartões')
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, update)

    def test_category_remove(self):
        """testing Category remove"""
        self.store.add(Category(u'Casa'))
        self.store.commit()
        cat = self.store.find(Category, Category.name == u'Casa').one()
        self.store.remove(cat)
        self.assert_(self.store.find(Category, Category.name == u'Casa').one() is None)

    def test_category_by_rule(self):
        """testing Category retrieval by CategoryRule"""
        # -- inserting category
        cat = self.store.find(Category, Category.name.like(u'Auto%')).one()
        cat.rules.add(self.store.add(CategoryRule(ur'POSTO')))
        self.store.commit()
        # -- inserting category
        statements = self.parser['StmtTrn']
        for statement in statements:
            cat2 = Category.by_rule(statement['memo'])
            if bool(cat2): break
        self.assertEqual(cat2.name, cat.name)
        
    def test_category_rule_insertion(self):
        """testing CategoryRule insertion"""
        # this code inserts category rules
        cat = self.store.find(Category, Category.name.like(u'Auto%')).one()
        cat_rule = CategoryRule(ur'POSTO', cat)
        self.assertEqual(cat_rule.category, cat)
        self.assertEqual(self.store.find(CategoryRule).count(), 1)

        from sqlite3 import IntegrityError
        cat_rule = CategoryRule(ur'POSTO', cat)
        self.assertRaises(IntegrityError, self.store.commit)
    
    def test_category_rule_find_by_regex(self):
        """testing CategoryRule insertion"""
        # this code inserts category rules
        cat = self.store.find(Category, Category.name.like(u'Auto%')).one()
        cat_rule = CategoryRule(ur'POSTO', cat)
        self.assertEqual(cat_rule.category, cat)
        self.assertEqual(self.store.find(CategoryRule).count(), 1)
        self.assertEqual(CategoryRule.by_regex(ur'POSTO'), cat_rule)
    
    def test_category_add_rule(self):
        """testing Category add_rule"""
        # this code inserts category rules
        cat = self.store.find(Category, Category.name.like(u'Auto%')).one()
        cat.add_rule(ur'POSTO')
        self.assertEqual(cat.rules.count(), 1)
        self.assertEqual(self.store.find(CategoryRule).count(), 1)
        self.assertEqual(self.store.find(CategoryRule, CategoryRule.regex == ur'POSTO').one().category, cat)
    

class TestBankAccount(TestDB):
    '''Test BankAccount in salim database.'''

    def test_bank_account(self):
        """testing BankAccount insertion"""
        # creating BankAccount
        d = {
        'bankid': int(self.parser['bankid']),
        'branch': self.parser['branchid'],
        'account': self.parser['acctid']
        }
        bankacc = BankAccount(**d)
        self.store.add(bankacc)
        self.assertEqual(bankacc.bankid, 1)
        self.assertEqual(bankacc.branch, u'3520-3')
        self.assertEqual(bankacc.account, u'14329-4')
        self.assert_(bankacc.name is None)
        # self.store.commit()
        self.assertEqual(self.store.find(BankAccount).count(), 1)
    
    def test_bank_account_double_insertion(self):
        """testing BankAccount double insertion: IntegrityError on commit"""
        # creating BankAccount
        d = {
        'bankid': int(self.parser['bankid']),
        'branch': self.parser['branchid'],
        'account': self.parser['acctid']
        }
        bankacc = BankAccount(**d)
        self.store.add(bankacc)
        self.store.commit()
        # creating BankAccount again!
        p = [int(self.parser['bankid']), self.parser['acctid'], self.parser['branchid']]
        bankacc = BankAccount(*p)
        self.store.add(bankacc)
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, self.store.commit)
    
    def test_bank_account_find(self):
        """testing BankAccount find missing BankAccount"""
        # testing BankAccount
        bankacc = self.store.get(BankAccount, self.parser['acctid'])
        self.assertEqual(bankacc, None)
    

class TestBalance(TestDB):
    """Class for unit tests on Balance"""

    def setUp(self):
        """docstring for setUp"""
        super(TestBalance, self).setUp()
        self.bankacc = self._get_bank_account(self.parser)
    
    def test_balance(self):
        """testing LedgerBalance insertion"""
        # testing LedgerBalance
        info = self.parser['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': self.parser['acctid']
        }
        bal = LedgerBalance(**d)
        self.store.add(bal)
        self.assertEqual(bal.id, None) # at this time id must be None
        balance = LedgerBalance.by_bank_account_and_date(self.bankacc, str2date(self.parser['ledgerbal']['dtasof']))
        self.assertNotEqual(bal.id, None) # at this time id must not be None

        self.assertEqual(balance.bank_account.bankid, 1)
        self.assertEqual(balance.amount, 0.0)
        self.assertEqual(balance.date, str2date('20080528'))

    def test_balance_double_insertion(self):
        """testing LedgerBalance double insertion"""
        info = self.parser['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': self.bankacc
        }
        LedgerBalance(**d)
        LedgerBalance(**d)
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, self.store.commit)
    
    def test_null_account(self):
        """testing LedgerBalance insertion with null bank account: Integrity error on commit."""
        info = self.parser['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt'])
        }
        balance = LedgerBalance(**d)
        self.store.add(balance)
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, self.store.commit)
    
    def test_null_account2(self):
        """testing LedgerBalance insertion and retrieval with null bank account: No commit, IntegrityError on find."""
        info = self.parser['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt'])
        }
        balance = LedgerBalance(**d)
        self.store.add(balance)
        def find():
            self.store.find(LedgerBalance, LedgerBalance.date == str2date(self.parser['ledgerbal']['dtasof'])).one()
        from sqlite3 import IntegrityError
        self.assertRaises(IntegrityError, find)
    
    def test_last_balance(self):
        """testing LedgerBalance.last()"""
        # testing LedgerBalance
        balance1 = LedgerBalance(**{'date': str2date('20080528'), 'amount': 5.0, 'bank_account': self.bankacc})
        balance2 = LedgerBalance(**{'date': str2date('20080529'), 'amount': 2.0, 'bank_account': self.bankacc})
        self.assertEqual(self.store.find(LedgerBalance).count(), 2)
        self.assertEqual(LedgerBalance.last().id, balance2.id)
    

class TestStatement(TestDB):
    """Class for testing Statements"""

    def setUp(self):
        """docstring for setUp"""
        super(TestStatement, self).setUp()
        self.bankacc = self._get_bank_account(self.parser)
        self.balance = self._get_balance(self.parser['ledgerbal'], self.bankacc)
        self.category = self.store.get(Category, u'Automóvel')
    
    def test_statements(self):
        """testing StatementTransaction"""
        statements = self.parser['StmtTrn']
        len_stmt = len(statements)
        for statement in statements:
            stmt = self._get_statement(statement, self.balance, self.category)
        # from sqlite3 import IntegrityError
        # self.assertRaises(IntegrityError, self._get_statement, statement, self.balance, self.bankacc, self.category)
    
    def test_statements_insertion_with_category_rule(self):
        """testing StatementTransaction with category rules with another thin API"""
        # -- inserting category rule POSTO
        cat = self.store.find(Category, Category.name.like(u'Auto%')).one()
        cat.rules.add(self.store.add(CategoryRule(ur'POSTO')))
        self.store.commit()
        # --
        statements = self.parser['StmtTrn']
        for transaction in statements:
            param = {
                'date' : str2date(transaction['dtposted']),
                'amount' : float(transaction['trnamt']),
                'memo' : transaction['memo'],
                'checknum' : transaction['checknum'],
                'fitid' : transaction['fitid']
            }
            tr = StatementTransaction(**param)
            tr = self.balance.add_transaction(tr)
            self.assertEqual(tr.balance.id, self.balance.id)


class TestEntireOFXInsertion(TestDB):
    def test_ofx_insertion(self):
        """testing OFX insertion with two consecutive days"""
        # -- bank account
        d = {
        'bankid': int(self.parser1['bankid']),
        'branch': self.parser1['branchid'],
        'account': self.parser1['acctid']
        }
        bankacc = self.store.get(BankAccount, self.parser1['acctid'])
        if not bool(bankacc):
            bankacc = BankAccount(**d)
            self.store.add(bankacc)
        # -- balance 1
        info = self.parser1['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': bankacc
        }
        balance1 = LedgerBalance(**d)
        statements = self.parser1['StmtTrn']
        for transaction in statements:
            param = {
                'date' : str2date(transaction['dtposted']),
                'amount' : float(transaction['trnamt']),
                'memo' : transaction['memo'],
                'checknum' : transaction['checknum'],
                'fitid' : transaction['fitid']
            }
            tr = StatementTransaction(**param)
            tr = balance1.add_transaction(tr)
            if bool(tr):
                self.assertEqual(tr.balance, balance1)
        # -- balance 2
        info = self.parser2['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': bankacc
        }
        balance2 = LedgerBalance(**d)
        statements = self.parser2['StmtTrn']
        null       = 0
        for transaction in statements:
            param = {
                'date' : str2date(transaction['dtposted']),
                'amount' : float(transaction['trnamt']),
                'memo' : transaction['memo'],
                'checknum' : transaction['checknum'],
                'fitid' : transaction['fitid']
            }
            tr = StatementTransaction(**param)
            tr = balance2.add_transaction(tr)
            if bool(tr):
                self.assertEqual(tr.balance.id, balance2.id)
            else:
                null += 1
        self.assertEqual(null, 3)
        self.assertEqual(balance2.is_valid(), True)
    
    def test_ofx_insertion2(self):
        """testing OFX insertion with two consecutive days that don't match"""
        # -- bank account
        d = {
        'bankid': int(self.parser1['bankid']),
        'branch': self.parser1['branchid'],
        'account': self.parser1['acctid']
        }
        bankacc = self.store.get(BankAccount, self.parser1['acctid'])
        if not bool(bankacc):
            bankacc = BankAccount(**d)
            self.store.add(bankacc)
        # -- balance 1
        info = self.parser1['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': bankacc
        }
        balance1 = LedgerBalance(**d)
        statements = self.parser1['StmtTrn']
        for transaction in statements:
            param = {
                'date' : str2date(transaction['dtposted']),
                'amount' : float(transaction['trnamt']),
                'memo' : transaction['memo'],
                'checknum' : transaction['checknum'],
                'fitid' : transaction['fitid']
            }
            tr = StatementTransaction(**param)
            tr = balance1.add_transaction(tr)
            if bool(tr):
                self.assertEqual(tr.balance, balance1)
        self.store.commit()
        # -- balance 2
        info = self.parser2['ledgerbal']
        d = {
        'date': str2date(info['dtasof']),
        'amount': float(info['balamt']),
        'bank_account': bankacc
        }
        balance2           = LedgerBalance(**d)
        balance2.amount   -= 1
        statements         = self.parser2['StmtTrn']
        null               = 0
        for transaction in statements:
            param = {
                'date' : str2date(transaction['dtposted']),
                'amount' : float(transaction['trnamt']),
                'memo' : transaction['memo'],
                'checknum' : transaction['checknum'],
                'fitid' : transaction['fitid']
            }
            tr = StatementTransaction(**param)
            tr = balance2.add_transaction(tr)
            if bool(tr):
                self.assertEqual(tr.balance.id, balance2.id)
            else:
                null += 1
        self.assertEqual(self.store.find(LedgerBalance).count(), 2)
        self.assertEqual(balance2.is_valid(), False)
        self.store.rollback()
        self.assertEqual(self.store.find(LedgerBalance).count(), 1)
    


class TestBudgetEntry(TestDB):
    """Test BudgetEntry in salim database"""
    def test_budget_entry_insertion(self):
        """testing BudgetEntry insertion with None category"""
        entry = BudgetEntry(u'Credicard',str2date('20080701'), 2.00)
        self.store.add(entry)
        self.assertEqual(entry.id, None) # at this time id must be None!
        self.assertEqual(entry.name, u'Credicard')
        self.assertEqual(entry.date, str2date('20080701'))
        self.assertEqual(entry.amount, 2.00)
        self.store.commit()
        self.assertNotEqual(entry.id, None)    # at this time id must not be None!
    
    def test_budget_entry_insertion_with_category(self):
        """testing BudgetEntry insertion with category"""
        cat = self.store.get(Category, u'Empregada')
        entry = BudgetEntry(u'Credicard',str2date('20080701'), 2.00, cat)
        self.assertEqual(entry.id, None) # at this time id must be None!
        self.assertEqual(entry.name, u'Credicard')
        self.assertEqual(entry.date, str2date('20080701'))
        self.assertEqual(entry.amount, 2.00)
        self.assertEqual(entry.category.name, u'Empregada')
        self.store.commit()
        self.assertNotEqual(entry.id, None)    # at this time id must not be None!
    

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(makeSuite(TestOFXParser))
    suite.addTest(makeSuite(TestOFXFileParser))
    suite.addTest(makeSuite(TestCategory))
    suite.addTest(makeSuite(TestBankAccount))
    suite.addTest(makeSuite(TestBalance))
    suite.addTest(makeSuite(TestStatement))
    suite.addTest(makeSuite(TestEntireOFXInsertion))
    suite.addTest(makeSuite(TestBudgetEntry))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
