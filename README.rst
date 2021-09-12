==============================================
 Customer Relationship Management Application
==============================================

Description
===========

This program provides a graphical user interface for the management of tenants in a London letting agency.

Features
--------

* Allow querying of tenant information by property identification
* Provides list of documents sent to tenents by email
* Allows printing of list of documents sent to tenant
* Provides a validated entry form to ensure correct data
* Provides import and export functions for data

Author
======
Angelo Varlotta, 2021

Requirements
============

* Python 3
* Tkinter
* PostgreSQL

Usage
=====

To start the application, run:

   python crm_app/crm_app.py

General Notes
=============

The main data entry form contains office, property, tenant information and list of documents sent by email. The first pane lists the property ID and landlord company of the flat. The second pane lists information on the flat: number, address, post code and city. The third pane lists tenant information: first name, last name and email. Finally, the fourth pane shows the list of documents sent by email. Visually the data entry form would look something like this.

+--Office information------------------+
|   Property ID   |  Landlord company  |
+--Property information----------------+
|  Flat # | Address | Post code | City |
+--Tenant information------------------+
|  First name  |  Last Name  |  Email  |
+--List of documents sent by email-----+
|  Email - Document #1                 |
|  Email - Document #2                 |
|  Email - Document #3                 |
|  (...)                               |
+--------------------------------------+
