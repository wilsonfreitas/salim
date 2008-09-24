#!/usr/bin/env python
# encoding: utf-8
"""
mydbTest.py

Created by Wilson Freitas on 2008-08-29.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from unittest import *

class TestMyDB(TestCase):
    '''Test my database -- wrapper functions to storm module'''
    def setUp(self):
        """docstring for setUp"""
        mydb.create_database('sqlite:../database/salim.db')
        mydb.read_file('../database/salim.sql')
