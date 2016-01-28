#!/bin/python
""" Import script for a specific format of yodiz board from a user.

THIS ONE IS A QUICK HACK WITH MINOR CHANGES FROM THE NON-BACKLOG VERSION

Some notes:
  Backlog has all user stories, have to filter out stories in sprints.
  Sprint exports have user stories plus tasks/bugs

  Backlog export Columns:
    0 Position
    1 Id
    2 Title
    3 Type
    4 DescriptionPlainText
    5 Points
    6 Effort Estimated
    7 Effort Remaining
    8 Effort Spent
    9 Status
    10 Created by
    11 Created on
    12 Responsible
    13 Sprint
    14 Release
    15 Component
    16 Epic
    17 Due Date
    18 Priority
    19 Severity
    20 Followers
    21 Other Responsibles
    22 Tags
    23 US-Contains DB Changes
    24 US-Release Note
    25 User Story Id
    26 User Story Title


  Sprint export Columns:
    0-19 Same as backlog
    20 Issue Priority
    21 Followers
    22 Other
    23 Responsibles
    24 Tags
    25 Steps To Reproduce
    26 US-Contains DB Changes
    27 US-Release Note
    28 BG-Release Note
    29 User Story Id
    30 User Story Title

"""

import slumber
from colorama import init, Fore, Back, Style
from time import sleep
import local_settings as settings
import json
import re
import csv

import logging
from import_util import ScrumDoImport

epics = ( ('EP-4' , 'Purchase Offer System'),
            ('EP-23' , 'Mobile App (Phone)'),
            ('EP-12' , 'Sales Queue 1.1'),
            ('EP-14' , 'Freight Management'),
            ('EP-11' , 'Price Prediction'),
            ('EP-19' , 'Invoice System'),
            ('EP-34' , 'Sales Queue 2.0'),
            ('EP-31' , 'General DCC pages'),
            ('EP-22' , 'Telemarketing System'),
            ('EP-30' , 'General DCC Pages Needing .NET'),
            ('EP-29' , 'Quote System'),
            ('EP-26' , 'Marketing'),
            ('EP-28' , 'Contact/Customer Section Updates'),
            ('EP-25' , 'Employee List and Settings'),
            ('EP-21' , 'Trigger Based Marketing (Alerts/Loop)'),
            ('EP-5' , 'Reports & Metrics'),
            ('EP-13' , 'Purchasing Queue'),
            ('EP-27' , 'Side Projects'),
            ('EP-24' , 'Brokered Shipping App'),
            ('EP-6' , 'Warehouse Management App'),
            ('EP-20' , 'Engineering Questions'),
            ('EP-16' , 'Internal Listing Process'),
            ('EP-32' , 'Sigma Surplus (Ebay)'),
            ('EP-9' , 'Document Library'),
            ('EP-3' , 'Customer Registration System'),
            ('EP-15' , 'Site Visit Planning (Acquisitions Dept)'),
            ('EP-17' , 'Shop Workorder / Tracking'),
            ('EP-33' , 'User List Chrome Extension'),
            ('EP-8' , 'CtrlCenter Equipment Pages'))

def main():
    importer = ScrumDoImport(settings.scrumdo_host,
                             settings.scrumdo_username,
                             settings.scrumdo_password,
                             settings.organization_slug,
                             settings.import_project_slug)

    api = importer.api_project



    for epic in epics:
        e = api.epics.post({'summary':"%s (%s)" % (epic[1], epic[0])})
        print "('%s','%s')" % (epic[0], e['id'])


if __name__ == "__main__":
    main()
