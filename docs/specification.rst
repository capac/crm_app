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
