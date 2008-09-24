
from storm.locals import *

class Person(object):
    __storm_table__ = 'person'
    name = Unicode(primary=True)
    age = Int()

class Friend(object):
    __storm_table__ = 'friend'
    name = Unicode(primary=True)
    age = Int()
    friend_name = Unicode()
    friend = Reference(friend_name, Person.name)

database = create_database("sqlite:")
store = Store(database)

store.execute("create table person (name varchar primary key, age integer)")
store.execute("create table friend (name varchar primary key, age integer, friend_name)")

wilson = Person()
wilson.name = u'Wilson'
wilson.age = 32

lissa = Friend()
lissa.name = u'Lissa'
lissa.age = 31
lissa.friend = u'Wilson'

store.add(wilson)
store.add(lissa)

print lissa.friend.name
