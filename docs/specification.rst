===============================================
 Chalk Farm Investments Data Query Application
===============================================

Description
-----------

The program is being created to address the issue of documents sent to tenants by emails, for the support of legal disputes.


Functionality required
----------------------

The program must:

* allow the query of tenant information by property identification
* create a list of documents sent by email to the tenant
* allow the printing of the list of documents
* import/export functionality of property information in database
* new/edit/delete functionality for property entries in database

Table entries
-------------

+-----------------------------------------------------------+
| Field       | Datatype  | Description                     |
+=============+===========+=================================+
| Property ID | String    | Property identification         |
+-----------------------------------------------------------+
| Landlord ID | String    | Landlord Company identification |
+-----------------------------------------------------------+
| Flat Number | String    | Street number for flat          |
+-----------------------------------------------------------+
| Address     | String    | Address for flat                |
+-----------------------------------------------------------+
| Post code   | String    | Post code for flat              |
+-----------------------------------------------------------+
| City        | String    | City the flat is in             |
+-----------------------------------------------------------+
| First name  | String    | First name of tenant            |
+-----------------------------------------------------------+
| Last Name   | String    | Last name of tenant             |
+-----------------------------------------------------------+
| Email       | String    | Email of tenant                 |
+-----------------------------------------------------------+
| Documents   | String    | List of documents               |
+-----------------------------------------------------------+
