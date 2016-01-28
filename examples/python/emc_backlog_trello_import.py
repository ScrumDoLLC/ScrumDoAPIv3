""" Import script for a specific format of trello board from a user.

A few interesting things:
 1. Points are in the name of the card
 2. This one is just for the backlog, no cells

"""

import slumber
from colorama import init, Fore, Back, Style
from time import sleep
import local_settings as settings
import json
import re

import logging
from import_util import ScrumDoImport


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

TRELLO_COLORS = {
    "black": 0x000000,
    "sky": 0x6D8FB4,
    "green": 0x2ABC9C,
    "blue": 0x3B98DB,
    "pink": 0x9959B4,
    "purple": 0x9959B4,
    "orange": 0xF4764E,
    "lime": 0x39CC74,
    "red": 0xA50C02,
    "yellow": 0xFEC54C
}



# See _card_list_id for info on this below
magic_labels = ["5601cf9a7a9be563fefe223b", "5601cfcf19ad3a5dc289e2d1"]


def main():
    init()
    importer = ScrumDoImport(settings.scrumdo_host,
                             settings.scrumdo_username,
                             settings.scrumdo_password,
                             settings.organization_slug,
                             settings.import_project_slug)

    with open(settings.import_json) as fp:
        import_data = json.load(fp)

    for id, username in settings.import_user_mappings.iteritems():
        importer.add_assignee_mapping(id, username)

    for label in import_data['labels']:
        importer.add_label(label['id'], label['name'], TRELLO_COLORS[label['color']])





    cards = {}
    for import_card in import_data['cards']:

        # In our sample data, the data has # of points in the name field, so extract that.
        match = re.search('^\(([0-9]+)\)\w*(.*)', import_card['name'])
        points = '?'
        summary = import_card['name']
        if match:
            points = match.group(1)
            summary = match.group(2)
        external_card_id = import_card['id']
        properties = {
           # "rank": rank,
           # "extra_1": None,
           # "extra_2": None,
           # "extra_3": None,
           # "epic_id": None,
           # "assignees": [],
           # "tags": "tag1, tag2",
           # "category": "",
           "detail": ScrumDoImport.to_html(import_card['desc']),
           "summary":  ScrumDoImport.to_html(summary),
           "points": points,
           "due_date": None if import_card['due'] is None else import_card['due'][:10]
        }
        importer.add_card(external_card_id, properties)
        # external_cell_id = _card_list_id(import_card)
        # importer.set_cell(external_card_id, external_cell_id)
        importer.set_labels(external_card_id, import_card['idLabels'])
        importer.set_assignees(external_card_id, import_card['idMembers'])
        for attachment in import_card['attachments']:
            name = attachment['name']
            url = attachment['url']
            importer.add_attachment_by_url(external_card_id, url, name)

    # Trello has these things called checklists which are separate from the card data, lets
    # jam them into the extra_1 field!  We'll format them like so:
    # [ ] Item 1
    # [ ] Item 2
    # [X] A compeleted item
    for import_checklist in import_data['checklists']:
        external_card_id = import_checklist['idCard']
        items = import_checklist['checkItems']
        name = import_checklist['name']
        if name == 'Tasks':
            for task in items:
                importer.add_task(external_card_id, task['name'])
        else:
            def _state(item):
                return '[X] ' if item['state'] == 'complete' else '[ ] '
            value = "\n".join([_state(item) + item['name'] for item in items])
            importer.set_card_property(external_card_id, 'extra_1',  ScrumDoImport.to_html(value) )

    # Now, add comments in
    for import_action in import_data['actions']:
        if import_action['type'] == 'commentCard':
            author = import_action['memberCreator']['id']
            text = import_action['data']['text']
            external_card_id = import_action['data']['card']['id']
            date = import_action['date']
            importer.add_comment(external_card_id, date, text, author)

    importer.create_iteration('Product Backlog')
    importer.import_all()


def _card_list_id(card):
    """For this import, the original project was using labels to differentiate between work types.
       But in the new project, we want to use rows on the board.

       So we're going to modify what cell a card goes into by rewriting the list id.

       Instead of just basing it off the list the card is in, we're going to combine
       it with two special labels that are on that card.
    """
    for label in card['idLabels']:
        if label in magic_labels:
            return card['idList'] + label
    return card['idList']




if __name__ == "__main__":
    main()