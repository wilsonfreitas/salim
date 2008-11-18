#!/usr/bin/env python
# encoding: utf-8
"""
csvadapter.py

Created by Wilson Freitas on 2008-09-17.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import csv
import re
import datetime
from operator import attrgetter, and_, eq

class AttributeParser(object):
    """docstring for AttributeParser"""
    def __init__(self):
        self.regexes = [(re.compile(v.__doc__), v) for k, v in self.__dict__ if v.__doc__]
    
    def parse(self, text):
        result = None
        for regex, func in self.regexes:
            match = regex.match(text)
            if match:
                result = func(text, match)
        if not result:
            result = parseAny(text)
        return result
    
    def parseNumber(self, text, match):
        r'^-?\s*\d+([\.,]\d+)?$'
        return eval(text)
    
    def parseBoolean(self, text, match):
        r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$'
        return eval(text.lower().capitalize())
    
    def parseText(self, text, match):
        r'^\''
        return text[1:]
    
    def parseAny(self, text):
        return text
    

class StormAttributeParser(AttributeParser):
    """docstring for StormAttributeParser"""
    def __init__(self, arg):
        super(StormAttributeParser, self).__init__()
    
    def parseText(self, text, match):
        r'^\''
        s = text[1:]
        s.decode('utf-8')
        return unicode(s)
    
    def parseDate(self, text, match):
        r'^\d?\d[/.-]\d\d[/.-]\d\d\d\d$'
        # dsr -- date separator regex
        dsr = re.compile(r'[/.-]')
        # dp -- date parts
        dp = dsr.split(text)
        return date( int(dp[2]), int(dp[1]), int(dp[0]) )
    
    def parseAny(self, text):
        return unicode(text.decode('utf-8'))
    

class CSVType(object):
    """docstring for CSVType"""
    def __init__(self, fields):
        self.typeName = fields[0]
        self.type = importClass(self.typeName)
        self.keys = {}
        self.attributes = {}
        self.statements = []
        self.hasPrimaryKey = False
        primaryKey = None
        for i, field in zip(count(1), fields[1:]):
            # TODO: resolve field names
            if re.match(r'^\{\w+\}$', field):
                self.keys[i] = field
            else:
                self.attributes[i] = field
            if isPrimaryKey(self.type, field):
                primaryKey = (i, field)
                if i in self.keys:
                    self.hasPrimaryKey = True
        if len(self.keys) is 0:
            if primaryKey is None:
                raise Exception("No key given")
            else:
                self.keys[primaryKey[0]] = primaryKey[1]
                self.hasPrimaryKey = True
                if primaryKey[0] in self.attributes:
                    del self.attributes[primaryKey[0]]
    
    def addStatement(self, statement):
        self.statements.append(statement)
    

class CSVStatement(object):
    """CSVStatement represents the csv statement to be executed by a ORM."""
    def __init__(self, csvRow, attrParser):
        self.csvRow = csvRow
        self.attributes = {}
        for i, field in zip(count(1), csvRow[1:]):
            self.attributes[i] = attrParser.parse(field)
    

class InsertCSVStatement(CSVStatement):
    """docstring for InsertCSVStatement"""
    def __init__(self, csvRow, attrParser):
        super(InsertCSVStatement, self).__init__(csvRow, attrParser)
    

class DeleteCSVStatement(CSVStatement):
    """docstring for InsertCSVStatement"""
    def __init__(self, csvRow, attrParser):
        super(DeleteCSVStatement, self).__init__(csvRow, attrParser)

class UpdateCSVStatement(CSVStatement):
    """docstring for InsertCSVStatement"""
    def __init__(self, csvRow, attrParser):
        super(UpdateCSVStatement, self).__init__(csvRow, attrParser)

class CSVStatementFactory(object):
    """docstring for CSVStatementFactory"""
    def newStatement(self, csvRow, attrParser):
        """docstring for newStatement"""
        if csvRow[0] == '+':
            return InsertCSVStatement(csvRow, attrParser)
        elif csvRow[0] == '-':
            return DeleteCSVStatement(csvRow, attrParser)
        elif csvRow[0] == '~':
            return UpdateCSVStatement(csvRow, attrParser)

class CSV(object):
    """CSV class that handles the csv files
        
    content is any iterable where the content of each row is data delimited text.
    """
    def __init__(self, content, attrParser=AttributeParser()):
        self.types = []
        for csvRow in csv.reader(content):
            csvRow = [f.strip() for f in csvRow]
            if len(csvRow) is 0 or csvRow[0][0] in ['#', '']:
                continue
            elif csvRow[0][0].isalpha():
                csvType = CSVType(csvRow)
                self.types.append(csvType)
            elif csvRow[0] in '+-~':
                statement = CSVStatementFactory.newStatement(csvRow, attrParser)
                csvType.addStatement(statement)

class ORM(object):
    """Abstracts the ORM engine"""
    def execute(self, csv):
        """Executes statements bound for all types attached to csv"""
        for typo in csv.types:
            for statement in typo.statements:
                self.executeStatement(typo, statement)

class StormORM(ORM):
    """docstring for StormORM"""
    def __init__(self, uri=None, store=None):
        from storm.locals import create_database, Store
        self.uri = uri
        self.store = store
        if self.uri:
            database = create_database(self.uri)
            self.store = Store(database)
        if not self.store:
            raise Exception('None storm store')
            
    def getObject(self, csvType, csvStatement):
        """Retrieves the object to be used at statement execution"""
        typo = csvType.type
        keys = csvType.keys
        attributes = csvStatement.attributes
        if type(csvStatement) in [DeleteCSVStatement, UpdateCSVStatement]:
            if csvType.hasPrimaryKey:
                return self.store.get(csvType.type, attributes[csvType.primaryKey[0]])
            else:
                pred = And([Eq(typo, key, attributes[i]) for i,key in keys])
                result = self.store.find(typo, pred)
                if result.count() == 0:
                    return None
                elif result.count() == 1:
                    return result.one()
                else:
                    return [r for r in result]
        elif type(csvStatement) is InsertCSVStatement:
            return typo()
    
    def executeStatement(self, csvType, csvStatement):
        """Executes csv statement"""
        obj = getObject(csvType, csvStatement)
        objs = []
        if type(obj) is list:
            objs += obj
        else:
            objs.append(obj)
        for _obj in objs:
            self._executeStatement(_obj, csvType, csvStatement)
    
    def _executeStatement(self, obj, csvType, csvStatement):
        """Executes csv statement"""
        keys = csvType.keys
        attributes = csvType.attributes
        values = csvStatement.attributes
        if type(csvStatement) is InsertCSVStatement:
            pairs = [(key, values[i]) for i,key in keys]
            pairs += [(key, values[i]) for i,key in attributes]
            for key, value in pairs:
                setattr(obj, key, value)
            self.store.add(obj)
        elif type(csvStatement) is UpdateCSVStatement:
            pairs = [(key, values[i]) for i,key in attributes]
            for key, value in pairs:
                setattr(obj, key, value)
        elif type(csvStatement) is DeleteCSVStatement:
            self.store.remove(obj)
        self.commit()

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

def importClass(className):
    fields = className.split('.')
    modName = '.'.join(fields[:-1])
    clsName = fields[-1]
    module = __import__(modName, globals(), locals(), [clsName], -1)
    return getattr(module, clsName)

def isPrimaryKey(cls, attrName):
    if hasattr(getattr(cls, attrName), 'primary'):
        return True
    else:
        return False

def Eq(cls, name, value):
    f = attrgetter(name)
    return eq(f(cls), value)

def And(preds):
    return reduce(and_, preds)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

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
    r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$': lambda v: eval(v.lower().capitalize()),
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


