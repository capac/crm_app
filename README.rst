==============================================
 Customer Relationship Management Application
==============================================

Description
===========

This program provides a graphical user interface for the management of tenants in a London letting agency.

Author
======
Angelo Varlotta, 2021

Features
========

* Provides a validated entry form to ensure correct data
* Allows update of tenant information in property 
* Provides add / delete property functions
* Provides import and export functions for tenant data
* Provides list of documents sent by email to tenants
* Allows saving to CSV file of the list of documents sent to tenants

Requirements
============

* Python (>=3.8.x)
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately (`brew install python-tk@3.9`)),
* psycopg2 (>=2.8.6), install with `python -m pip install psycopg2` or `conda install psycopg2`,
* PostgreSQL (>=13.4), install with `brew install postgresql@13`,
* O365 (>=2.0.16), install with `python -m pip install O365`.

Configuration
=============

In order for the O365 package to work, you will need to follow the instructions in the O365 documentation (https://pypi.org/project/O365), especially at the 'Authentication Steps' paragraph. You will need to register the application on the Azure Portal and generate a new application client ID and client secret. Read the O365 documentation for more details.

Personal settings, such as the Microsoft account email, application client ID and client secret are saved in the 'settings.json file', which is created the first time the program is run and is located differently according to the platform: "~/Library/Application Support/CRMApp" for macOS and "~/AppData/Local/CRMApp" for Windows. Edit the file to add your personal settings.

If it's your first login to your account, you will have to visit a website to authenticate after which you need tp paste the redirected URL in the console. At that point, your token will be stored. If you already have a valid stored token, then the account is already considered authenticated and further operations can proceed.

Usage
=====

To start the application, run in the application root directory:
> python crm_app/crm_app.py

Issues
======

* Querying of tenant information by property identification still hasn't been implemented.

* The program first connects to the user's Microsoft Outlook/Exchange/Office 365 account to retrieve the sent emails, and so requires an internet connection to work. The program will fail if there is no internet connection, even though previous queries are saved locally to the database.

* Emails already present aren't updated, however sent emails deleted remotely aren't removed locally.

TODO
====

* Check button to remove emails with no attachments from the document list
* Bar chart showing tenant occupancy in the properties
* Bar chart showing number of properties per landlord
