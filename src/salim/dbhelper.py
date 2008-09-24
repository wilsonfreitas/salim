#!/usr/bin/env python
# encoding: utf-8
"""
db.py

Created by Wilson Freitas on 2008-08-24.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

def execute(store, statements):
    """Executes sql statements in one time"""
    if type(statements) is str:
        sql_statements = statements.split(';')
    else:
        sql_statements = iter(statements)
    for stmt in sql_statements:
        store.execute(stmt)
    store.commit()


def read_file(store, filename):
    '''Loads a database from sql statements of one file'''
    sql_file = file(filename)
    execute(sql_file.read())
    sql_file.close()


def str2date(dts):
    '''Converts string 'YYYYMMDD' to date'''
    from datetime import date
    return date( int(dts[0:4]), int(dts[4:6]), int(dts[6:8]) )
