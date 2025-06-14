==============================================
 Customer Relationship Management Application
==============================================

Description
===========

This program provides a graphical user interface for the management of tenants in a letting agency.

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
* Allows saving of the list of documents sent to tenants to a CSV file

Requirements
============

* Python (>=3.8.x),
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately ('brew install python-tk@3.9')),
* psycopg2 (>=2.8.6), install with 'python -m pip install psycopg2' or 'conda install psycopg2',
* PostgreSQL (>=13.4), install with 'brew install postgresql@13',
* O365 (>=2.0.16), install with 'python -m pip install O365',
* matplotlib (>=3.5.x), install with 'python -m pip install matplotlib'.

Configuration
=============

In order for the O365 package to work, you will need to follow the instructions in the O365 documentation (https://pypi.org/project/O365), especially at the 'Authentication Steps' paragraph. You will need to register the application on the Azure Portal and generate a new application client ID and client secret. Read the O365 documentation for more details.

Personal settings, such as the Microsoft account email, application client ID and client secret are saved in the 'settings.json' file, which is created the first time the program is run and is located differently according to the platform: "~/Library/Application Support/CRMApp" for macOS and "~/AppData/Local/CRMApp" for Windows. Edit the file to add your personal settings.

If it's your first login to your account, you will have to visit a Microsoft authentication website after which you need to paste the redirected URL into the terminal to have access to your email, and at that point your token will be stored. If you already have a valid token, then the account is already considered authenticated and further operations can proceed. As long as the token isn't older than 90 days, you won't need to go through the terminal authentication procedure again.

Usage
=====

To start the application, run from the application root directory the following command at the prompt:
> python crm_app/crm_app.py

Issues
======

* An internet connection is required for the program to work, if not it halts with an error message.

* Currently dark mode on macOS using Python 3.9.x uses inconsistent fonts and backgrounds. A dark theme mode needs to be implemented to fix the current issues. This may be solved by installing more themes, such as thoses in ttkthemes (currently at version 3.3.2). To install run 'python -m pip install ttkthemes'.

To do
=====

* Make sure on first run that PostgreSQL user and database are created without issue.
* Gracefully halt retrieval of remote emails if internet connection isn't avaiable.
* Add unit testing for code checking.
* Add a log parser and log file for debugging purposes.
* Use a dropdown menu at 'Property ID' to search for properties in main window.
