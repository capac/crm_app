==============================================
 Customer Relationship Management Application
==============================================

Description
===========

This program provides a graphical user interface for the management of tenants in a London letting agency.

Features
--------

* Allow querying of tenant information by property identification
* Provides list of documents sent to tenants by email
* Allows printing of list of documents sent to tenants
* Provides a validated entry form to ensure correct data
* Provides import and export functions for data
* Provides add / delete property functions
* Allow update of tenant information in property 

Author
======
Angelo Varlotta, 2021

Requirements
============

* Python 3.x
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately (`brew install python-tk@3.9`)),
* psycopg2, install with `python -m pip install psycopg2`,
* PostgreSQL (>=13.4), install with `brew install postgresql@13`,
* O365 (https://pypi.org/project/O365), install with `python -m pip install O365`.

Usage
=====

To start the application, run:

   python crm_app/crm_app.py
