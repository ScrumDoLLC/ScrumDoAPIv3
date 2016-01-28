#!/bin/python
""" Import script for a specific format of yodiz board from a user.

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

POINT_MAP = {
 'XS': 1,
 'S': 5,
 'M': 10,
 'L': 15,
 'XL': 25,
 'XXL': 25,
 '': '?'
}

epics = {
    'Purchase Offer System':'33466',
    'Mobile App (Phone)':'33467',
    'Sales Queue 1.1':'33468',
    'Freight Management':'33469',
    'Price Prediction':'33470',
    'Invoice System':'33471',
    'Sales Queue 2.0':'33472',
    'General DCC pages':'33473',
    'Telemarketing System':'33474',
    'General DCC Pages Needing .NET':'33475',
    'Quote System':'33476',
    'Marketing':'33477',
    'Contact/Customer Section Updates':'33478',
    'Employee List and Settings':'33479',
    'Trigger Based Marketing (Alerts/Loop)':'33480',
    'Reports & Metrics':'33481',
    'Purchasing Queue':'33482',
    'Side Projects':'33483',
    'Brokered Shipping App':'33484',
    'Warehouse Management App':'33485',
    'Engineering Questions':'33486',
    'Internal Listing Process':'33487',
    'Sigma Surplus (Ebay)':'33488',
    'Document Library':'33489',
    'Customer Registration System':'33490',
    'Site Visit Planning (Acquisitions Dept)':'33491',
    'Shop Workorder / Tracking':'33492',
    'User List Chrome Extension':'33493',
    'CtrlCenter Equipment Pages':'33494'
}

def main():
    init()
    iterations = (("G", "input/g.csv"),
                  ("Frodo", "input/frodo.csv"),
                  ("Ewok", "input/ewok.csv"),
                  ("Dexter Jettster", "input/de.csv"),
                  ("Chewbacca", "input/c.csv"),
                  ("Boss Nass", "input/b.csv"),
                  ("Ackbar", "input/ackbar.csv"),
                  ("Han Solo", "input/han_solo.csv"),
                  ("Harry Potter", "input/harry_potter.csv"),
                  ("Boba Fett", "input/boba_fett.csv"),
                  ("Darth Vader", "input/d.csv"),
                  ("Hellboy", "input/hellboy.csv"),
                  ("Old Man Sprint", "input/old_man.csv"),
                  ("PO System Sprint 3", "input/po_system.csv"))


    for iteration in iterations:
        import_iteration(iteration)



def import_iteration(iteration):
    logger.info("Importing iteration " + iteration[0])
    (iteration_name, iteration_file) = iteration

    importer = ScrumDoImport(settings.scrumdo_host,
                             settings.scrumdo_username,
                             settings.scrumdo_password,
                             settings.organization_slug,
                             settings.import_project_slug)

    for assignee in settings.assignees:
        importer.add_assignee_mapping(assignee[0], assignee[1])

    importer.add_label("issue", "Bug", 0xff0000)
    importer.add_label("userstory", "User Story", 0x00ff00)

    importer.set_cell_mapping("Completed", "Ready for Release")
    importer.set_cell_mapping("Done", "Released")
    importer.set_cell_mapping("In Testing", "QA")
    importer.set_cell_mapping("Blocked", "Work Queue")
    importer.set_cell_mapping("Planned", "Work Queue")
    importer.set_cell_mapping("Fixed", "Ready for Release")
    importer.set_cell_mapping("New", "Work Queue")
    importer.set_cell_mapping("Duplicate", "Work Queue")
    importer.set_cell_mapping("In Progress", "Developing")
    importer.set_cell_mapping("Accepted", "Ready for Release")
    importer.set_cell_mapping("Rejected", "Work Queue")


    with open(iteration_file, 'rb') as csvfile:
        logger.info("Reading %s" % iteration_file)
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            import_row(row, importer)


    importer.create_iteration(iteration_name)
    importer.import_all()

def import_row(row, importer):
    if row[3] in ("userstory", "issue"):
        import_card(row, importer)
    elif row[3] == "task":
        import_task(row, importer)
    else:
        logger.error("Don't know what to do with " + row[3])

def import_task(row, importer):
    logger.info("  Importing {id}".format(id=row[1]))
    try:
        minutes = int(row[6]) * 60
    except:
        minutes = 0
    importer.add_task(row[28], row[2], row[12], row[24], minutes, 10 if row[9] == 'Done' else 1)

def import_card(row, importer):
    logger.info("  Importing {id}".format(id=row[1]))
    try:
        rank = int(row[0]) * 1000
    except:
        rank = 1000

    tags = []

    # Converting some columns to tags:
    for col in (1,14,15,18,19,20,24):
        t = row[col]
        if len(t) > 0:
            tags.append(t)

    e = ScrumDoImport.to_html(row[26] + "\n" + row[27] + "\n" + row[28])

    try:
        minutes = int(row[6]) * 60
    except:
        minutes = 0

    properties = {
        "rank": rank,
        "epic_rank": rank,
        "extra_1": e,   # release notes
        # "extra_2": None,
        # "extra_3": None,
        "epic_id": epics.get(row[16], None),
        "tags": ",".join(tags),
        # "category": "",
        "estimated_minutes": minutes,
        "detail": ScrumDoImport.to_html(row[4]),
        "summary":  ScrumDoImport.to_html(row[2]),
        "points": POINT_MAP[row[5]],
        #"due_date": None if import_card['due'] is None else import_card['due'][:10]
    }

    importer.add_card(row[1], properties)
    importer.set_cell(row[1], row[9])
    importer.set_labels(row[1], [row[3]])

    if row[12] != '':
        importer.assign_card(row[1], row[12])





def setupLogging():
    logging.basicConfig(
        filename='import.log',
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S')

    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    logging.getLogger('').addHandler(console)
    return logging.getLogger(__name__)

logger = setupLogging()

if __name__ == "__main__":
    main()
