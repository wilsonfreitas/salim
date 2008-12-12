#!/usr/bin/python
# -*- encoding: latin1 -*-

import sys
sys.path.append('../src')

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
from salim.model import *
from datetime import date

from salim.csvadapter import *


class TestCSV(TestCase):
    csvContent = '''
salim.model.Category,Name, Parent
+                   ,Contas, Casa
+                   ,Despesas Operacionais, Casa
'''.split('\n')
    
    def test_CSV(self):
        """testing CSV"""
        csv = CSV(self.csvContent)
        self.assertEqual(len(csv.types), 1)
        self.assertEqual(len(csv.types[0].statements), 2)
        
    def test_CSVType(self):
        '''testing CSVType'''
        csv = CSV(self.csvContent)
        self.assertEqual(len(csv.types[0].keys), 1)
        self.assertEqual(len(csv.types[0].attributes), 1)
        
    

class TestAttributeParser(TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_AttributeParser(self):
        '''testing AttributeParser'''
        parser = AttributeParser()
        v = parser.parse('123')
        self.assertEqual(v, 123)
        v = parser.parse('01/01/2008')
        self.assertEqual(v, '01/01/2008')
        v = parser.parse("'123")
        self.assertEqual(v, '123')
        v = parser.parse("1.1")
        self.assertEqual(v, 1.1)
        v = parser.parse("TRUE")
        self.assertEqual(v, True)
        v = parser.parse("FALSE")
        self.assertEqual(v, False)
        v = parser.parse("wilson")
        self.assertEqual(v, 'wilson')
        
        
    def test_StormAttributeParser(self):
        '''testing StormAttributeParser'''
        parser = StormAttributeParser()
        v = parser.parse('123')
        self.assertEqual(v, 123)
        v = parser.parse('01/01/2008')
        self.assertEqual(v, date(2008, 1, 1))
        v = parser.parse("'123")
        self.assertEqual(v, u'123')
        v = parser.parse("1.1")
        self.assertEqual(v, 1.1)
        v = parser.parse("TRUE")
        self.assertEqual(v, True)
        v = parser.parse("FALSE")
        self.assertEqual(v, False)
        v = parser.parse("wilson")
        self.assertEqual(v, u'wilson')
        
        
        
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(makeSuite(TestAttributeParser))
    suite.addTest(makeSuite(TestCSV))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
