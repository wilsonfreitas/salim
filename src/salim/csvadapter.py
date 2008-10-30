#!/usr/bin/env python
# encoding: utf-8
"""
csvadapter.py

Created by Wilson Freitas on 2008-09-17.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import csv
import re

class ORM(object):
    """docstring for ORM"""
    def __init__(self, arg):
        super(ORM, self).__init__()
        self.arg = arg
        
    def execute(self, csv):
        """docstring for execute"""
        pass
        
    def executeCSVStatement(self, csvStatement):
        """docstring for executeCSVStatement"""
        pass
        

class StormORM(ORM):
    """docstring for StormORM"""
    def __init__(self, arg):
        super(StormORM, self).__init__()
        self.arg = arg
        
    def execute(self, csvText):
        """docstring for execute"""
        import csv
        for csvRow in csv.reader(csvText.split('\n')):
            csvRow = [f.strip() for f in csvRow]
            if len(csvRow) is 0 or csvRow[0][0] in ['#', '']:
                continue
            elif csvRow[0][0].isalpha():
                csvType = CSVType(csvRow)
            elif csvRow[0] in '-+~':
                # TODO: parse csvRow (use eval)
                # actions[ csvRow[0] ](handler, csvRow[1:], store)
                statement = CSVStatement(csvRow, csvType)
                self.executeCSVStatement(statement)
                
    def executeCSVStatement(self, csvStatement):
        """docstring for executeCSVStatement"""
        pass


class SQLObjectORM(ORM):
    """docstring for SQLObjectORM"""
    def __init__(self, arg):
        super(SQLObjectORM, self).__init__()
        self.arg = arg

class SQLAlchemyORM(ORM):
    """docstring for SQLAlchemyORM"""
    def __init__(self, arg):
        super(SQLAlchemyORM, self).__init__()
        self.arg = arg
        

def addAction(handler, csvRow, store):
    attrs = []
    attrs += handler.keys
    attrs += handler.attributes
    attrs = [(attrName, csvRow[i]) for i, attrName in attrs]

class Key(object):
    """docstring for KeyWrapper"""
    def __init__(self, keyName, isPrimaryKey):
        self.keyName = keyName
        self.isPrimaryKey = isPrimaryKey
        

class TypeHandler(object):
    """docstring for TypeHandler"""
    def __init__(self, typeRow):
        # TODO: replace split by real csv split
        fields = typeRow.split(',')
        self.typeName = fields[0]
        self.type = importClass(self.typeName)
        self.keys = []
        self.attributes = []
        primaryKey = None
        for i, field in zip(count(1), fields[1:]):
            # TODO: resolve field names
            if re.match(r'^\{\w+\}$', field):
                self.keys.append( (i, field) )
            else:
                self.attributes.append( (i, field) )
            if isPrimaryKey(self.type, field):
                primaryKey = (i, field)
        if len(self.keys) is 0:
            if primaryKey is None:
                raise Exception("No key given")
            else:
                self.keys.append( primaryKey )
                if primaryKey in self.attributes:
                    self.attributes.remove( primaryKey )


def importClass(className):
    fields = className.split('.')
    modName = '.'.join(fields[:-1])
    clsName = fields[-1]
    module = __import__(modName, globals(), locals(), [clsName], -1)
    return getattr(module, clsName)

def isPrimaryKey(cls, attrName):
    """docstring for isPrimaryKey"""
    if hasattr(getattr(cls, attrName), 'primary'):
        return True
    else:
        return False

def Eq(cls, name, value):
    f = attrgetter(name)
    return eq(f(cls), value)

def And(preds):
    return reduce(and_, preds)
        

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
    Convert human readable header names to property names. Examples:
    
    >>> resolve_property_name("Category")
    "category"
    >>> resolve_property_name("Bank Account")
    "bank_account"
    '''
    attr_name = str(attr_name).strip()
    attr_name = attr_name.lower()
    attr_name = re.sub('\s+', '_', attr_name)
    return attr_name


def resolve_camel_case_property_name(attr_name):
    '''
    Convert human readable header names to camel case property names. Examples:
    
    >>> resolve_property_name("Category")
    "category"
    >>> resolve_property_name("Bank Account")
    "bankAccount"
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


