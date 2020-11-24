(Design document staat in DESIGN.md)

# Application Name

This application creates an auction website that allows users to create auction listings, 
view active listings of other users, sort them by category and bid and comment on them.

## Getting Started

For this application to work, install the following:
Python3
pip
Django


**if the error 'Class has no objects member' occurs:**

pip3 install pylint-django

go to User Settings and add:

{"python.linting.pylintArgs": [
     "--load-plugins=pylint_django"
],}
