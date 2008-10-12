#!/usr/bin/env python
# encoding: utf-8
"""
csvadapter.py

Created by Wilson Freitas on 2008-09-17.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import csv
import re

def str2date(dts):
    '''Converts string 'YYYYMMDD' to date'''
    from datetime import date
    return date( int(dts[0:4]), int(dts[4:6]), int(dts[6:8]) )


def to_unicode(s):
    s = s.decode('utf-8')
    return unicode(s)

def parse_date(date_str):
    import re
    from datetime import date
    # dsr -- date separator regex
    dsr = re.compile(r'[/.-]')
    # dp -- date parts
    dp = dsr.split(date_str)
    return date( int(dp[2]), int(dp[1]), int(dp[0]) )

def parse_str(s):
    s = s[1:]
    s.decode('utf-8')
    return unicode(s)

parse_table = {
    r'^-?\s*\d+$': int,
    r'^-?\s*\d+[\.,]\d+$': float,
    r'^\d?\d[/.-]\d\d[/.-]\d\d\d\d$': parse_date,
    r'^\'': parse_str,
    r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$': lambda v: v.lower() == 'true',
    'any': to_unicode
}


def parse_value(v, parse_table=parse_table):
    v = str(v).strip()
    for regex, func in parse_table.iteritems():
        if re.match(regex, v): return func(v)
    return parse_table['any'](v)


def resolve_property_name(attr_name):
    '''
    Convert header human readable names to property names. Examples:
    
    * Category turns to category
    * Bank Account turns to bank_account
    '''
    attr_name = str(attr_name).strip()
    attr_name = attr_name.lower()
    attr_name = re.sub('\s+', '_', attr_name)
    return attr_name


def resolve_camel_case_property_name(attr_name):
    '''
    Convert header human readable names to property names. Examples:
    
    * Category turns to category
    * Bank Account turns to bankAccount
    '''
    attr_name = str(attr_name).strip()
    s = ''
    to_upper = False
    for c in attr_name:
        if c in '\t ':
            to_upper = True
            continue
        if to_upper:
            s += c.upper()
            to_upper = False
        else:
            s += c.lower()
    return s


def resolve_property_names(properties, camel_case=False):
    resolver = (camel_case and resolve_camel_case_property_name) or resolve_property_name
    return map(resolver, properties)


def update_model_instance(store, obj):
    db_obj = store.get(obj.__class__, getattr(obj, obj.__id__))
    for key,value in obj._storm_kwargs.iteritems():
        setattr(db_obj, key, value)
    return db_obj


def new_model_instance_with_parameter_less_init(typo, properties, values):
    from storm.properties import PropertyColumn
    from storm.references import Reference
    obj = typo()
    kwargs = {}
    for prop,value in zip(properties, values):
        if hasattr(typo, prop) and isinstance(getattr(typo, prop), (PropertyColumn, Reference)):
            if hasattr(getattr(typo, prop), 'primary') and getattr(typo, prop).primary:
                obj.__id__ = prop
            else:
                kwargs[prop] = value
        setattr(obj, prop, value)
    obj._storm_kwargs = kwargs
    return obj


def new_instance_with_parameter_less_init(typo, properties, values):
    obj = typo()
    for prop,value in zip(properties, values):
        setattr(obj, prop, value)
    return obj


def new_instance_with_kwargs_init(typo, properties, values):
    kwargs = {}
    for prop,value in zip(properties, values):
        kwargs[prop] = value
    return typo(**kwargs)
    

def create_new_instance(typo, properties, values, parameter_less=True):
    builder = (parameter_less and new_instance_with_parameter_less_init) or new_instance_with_kwargs_init
    return builder(typo, properties, values)


def parse_csv_file(csv_file, globals, camel_case=False, parameter_less=True, parse_table=parse_table):
    '''
    Read the csv file and instanciate objects.
    
    If only one entry point is enabled, the csv setting must be given here.
    '''
    objects = []
    for row in csv.reader(csv_file):
        row = [field.strip() for field in row]
        if len(row) == 0 or row[0].startswith('#') or (len(row) == 1 and row[0] == ''): # ignore comments and empty lines
            continue
        if bool(row[0]):
            typo, properties = globals[row[0]], resolve_property_names(row[1:], camel_case=camel_case)
        else:
            values = map(lambda v: parse_value(v, parse_table), row[1:])
            objects.append(create_new_instance(typo, properties, values, parameter_less))
    return objects


def parse_model_csv_file(csv_file, globals, camel_case=False, parameter_less=True, parse_table=parse_table):
    '''
    Read the csv file and instanciate objects.
    
    If only one entry point is enabled, the csv setting must be given here.
    '''
    objects = []
    for row in csv.reader(csv_file):
        row = [field.strip() for field in row]
        if len(row) == 0 or row[0].startswith('#') or (len(row) == 1 and row[0] == ''): # ignore comments and empty lines
            continue
        if bool(row[0]):
            typo, properties = globals[row[0]], resolve_property_names(row[1:], camel_case=camel_case)
        else:
            values = map(lambda v: parse_value(v, parse_table), row[1:])
            objects.append(new_model_instance_with_parameter_less_init(typo, properties, values))
    return objects


