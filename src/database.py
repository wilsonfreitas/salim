#!/usr/bin/python
# -*- encoding:utf-8 -*-

import storm
storm.database.DEBUG = True

from storm.locals import Store, create_database

DATABASE = create_database( "sqlite:salim.sqlite" )
STORE = Store( database )

def create_my_tables(store):
	global STORE

	STORE.execute( """ CREATE TABLE IF NOT EXISTS entry_template (
	                   id_entry_template INTEGER PRIMARY KEY,
	                   name VARCHAR UNIQUE,
	                   id_category INTEGER )
	                   """ )
	STORE.execute( """ CREATE TABLE IF NOT EXISTS category (
	                   id_category INTEGER PRIMARY KEY,
	                   id_parent INTEGER,
	                   name VARCHAR UNIQUE )
	                   """ )
	STORE.execute( """ CREATE TABLE IF NOT EXISTS budget_entry (
	                   id_budget_entry INTEGER PRIMARY KEY,
	                   id_entry_template INTEGER,
	                   entry_date TEXT,
	                   amount REAL )
	                   """ )
	STORE.execute( """ CREATE TABLE statement_transaction (
					   id_statement_transaction integer primary key,
					   memo varchar,
					   date text,
					   amount real,
					   ttype varchar,
				       checknum integer,
					   fitid integer )
					   """)
	STORE.commit()

