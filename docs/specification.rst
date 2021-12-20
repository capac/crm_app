===============================================
 Chalk Farm Investments Data Query Application
===============================================

Description
===========

The program is being created to address the issue of documents sent to tenants by emails,
for the support of legal disputes.


Functionality required
======================

The program must:

* allow the query of tenant information by property identification
* create a list of documents sent by email to the tenant
* allow the saving of the list of documents to a CSV file
* import / export functionality of property / tenant information in database
* new / edit / delete functionality for property / tenant entries in database

Table entries
=============

Property / Tenant view table
----------------------------

+------------------------------------------------------------------------+
|  Field                |   Datatype  |  Description                     |
+=======================+=============+==================================+
|  Property ID          |   String    |  Property identification         |
+------------------------------------------------------------------------+
|  Landlord ID          |   String    |  Landlord Company identification |
+------------------------------------------------------------------------+
| # Properties Building |   Integer   |  Number of flats in the building |
+------------------------------------------------------------------------+
|  Flat Number          |   String    |  Street number for flat          |
+------------------------------------------------------------------------+
|  Address              |   String    |  Address for flat                |
+------------------------------------------------------------------------+
|  Post code            |   String    |  Post code for flat              |
+------------------------------------------------------------------------+
|  City                 |   String    |  City the flat is in             |
+------------------------------------------------------------------------+
|  First name           |   String    |  First name of tenant            |
+------------------------------------------------------------------------+
|  Last Name            |   String    |  Last name of tenant             |
+------------------------------------------------------------------------+
|  Email                |   String    |  Email of tenant                 |
+------------------------------------------------------------------------+

Document / Tenant view table
----------------------------
 
+--------------------------------------------------------------+
| Field         | Datatype  | Description                      |
+===============+===========+==================================+
| Subject       | String    | Subject of email to tenant       |
+--------------------------------------------------------------+
| Email         | String    | Email of tenant                  |
+--------------------------------------------------------------+
| Date sent     | ISO Date  | Date email sent to tenant        |
+--------------------------------------------------------------+
| Date received | ISO Date  | Date email sent to tenant        |
+--------------------------------------------------------------+
| Document      | String    | List documents attached to email |
+--------------------------------------------------------------+
