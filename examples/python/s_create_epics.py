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

epics = (   ('EP-4' , 'EPIC EP-4 DESCRIPTION'),
            ('EP-23' , 'EPIC EP-23 DESCRIPTION'),
            ('EP-12' , 'EPIC EP-12 DESCRIPTION'),
            ('EP-14' , 'EPIC EP-14 DESCRIPTION'),
            ('EP-11' , 'EPIC EP-11 DESCRIPTION'),
            ('EP-19' , 'EPIC EP-19 DESCRIPTION'),
            ('EP-34' , 'EPIC EP-34 DESCRIPTION'),
            ('EP-31' , 'EPIC EP-31 DESCRIPTION'),
            ('EP-22' , 'EPIC EP-22 DESCRIPTION'),
            ('EP-30' , 'EPIC EP-30 DESCRIPTION'),
            ('EP-29' , 'EPIC EP-29 DESCRIPTION'),
            ('EP-26' , 'EPIC EP-26 DESCRIPTION'),
            ('EP-28' , 'EPIC EP-28 DESCRIPTION'),
            ('EP-25' , 'EPIC EP-25 DESCRIPTION'),
            ('EP-21' , 'EPIC EP-21 DESCRIPTION'),
            ('EP-5' , 'EPIC EP-5 DESCRIPTION'),
            ('EP-13' , 'EPIC EP-13 DESCRIPTION'),
            ('EP-27' , 'EPIC EP-27 DESCRIPTION'),
            ('EP-24' , 'EPIC EP-24 DESCRIPTION'),
            ('EP-6' , 'EPIC EP-6 DESCRIPTION'),
            ('EP-20' , 'EPIC EP-20 DESCRIPTION'),
            ('EP-16' , 'EPIC EP-16 DESCRIPTION'),
            ('EP-32' , 'EPIC EP-32 DESCRIPTION'),
            ('EP-9' , 'EPIC EP-9 DESCRIPTION'),
            ('EP-3' , 'EPIC EP-3 DESCRIPTION'),
            ('EP-15' , 'EPIC EP-15 DESCRIPTION'),
            ('EP-17' , 'EPIC EP-17 DESCRIPTION'),
            ('EP-33' , 'EPIC EP-33 DESCRIPTION'),
            ('EP-8' , 'EPIC EP-8 DESCRIPTION'))

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
