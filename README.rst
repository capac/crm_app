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

* Python (>=3.8.x)
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately (`brew install python-tk@3.9`)),
* psycopg2 (>=2.8.6), install with `python -m pip install psycopg2` or `conda install psycopg2`,
* PostgreSQL (>=13.4), install with `brew install postgresql@13`,
* O365 (>=2.0.16), install with `python -m pip install O365`.

Installation
============
In order for the O365 package to work, you will need to follow the instructions in the O365 documentation (https://pypi.org/project/O365), especially at the 'Authentication Steps' paragraph. You will need to register the application on the Azure Portal and generate a new application client ID and client secret. Read the documentation for more details.

Usage
=====

To start the application, run:

   python crm_app/crm_app.py
