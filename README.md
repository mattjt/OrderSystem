MORTWebsite
------------
A slightly less site.py-ish CMS with moderately sane modularity.

----------

**Required Software**
-----------------
> - **Python 2.7.9~2.7.10**
> - Dependencies in **requirements.txt**
> - PostgreSQL
> - Bower

----------

**Setup Instructions**
------------------
   
Create database tables by executing scripts in **Migrations** directory in version sequential order

Grab required libraries with bower (Required for using site with CDN mode disabled):
> bower install

Configure initial user and administrator subteam:
> python configure.py

Run the development server:
> python run.py