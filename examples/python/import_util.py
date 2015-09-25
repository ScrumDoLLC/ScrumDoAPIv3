from collections import defaultdict
import slumber
import os
import urllib2
import requests
import logging

logger = logging.getLogger(__name__)


class ScrumDoImport:
    """A utility class for importing data from other systems into ScrumDo.
       It works in two phases, first you gather up all the data to be imported.
       Then you call the import_all() method to actually write out the data.
       This class is designed to import a single iteration, so if you have more
       than one to do, create multiple instances of it."""

    def __init__(self,scrumdo_host,
                      scrumdo_username,
                      scrumdo_password,
                      organization_slug,
                      import_project_slug):

        # Some maps from external system to scrumdo
        self.assignee_mapping = {}  # Map from external user id -> scrumdo username
        self.label_mapping = {}  # Map from external label id to scrumdo label id
        self.cell_mapping = {}  # Map from external cell/column/status to scrumdo cell id
        self.board_cells = None

        # Data about cards we're going to import
        self.assignees = defaultdict(list)   # assignees[external_id] = [external_assignee, external_assignee2, ...]
        self.attachments = defaultdict(list)   # attachments[external_id] = [filename, filename2, filename3]
        self.comments = defaultdict(list)  # comments[external_id] = [{author, comment, date}, {}, ...  ]

        self.card_properties = {}

        self.api_iteration = None

        base_url = "%s/api/v3/" % scrumdo_host

        # On my local dev-server, keep alive doesn't work
        session = requests.session()
        session.keep_alive = False

        self.api = slumber.API(base_url, auth=(scrumdo_username, scrumdo_password), session=session)

        # Project API helper:
        self.api_project = self.api.organizations(organization_slug).projects(import_project_slug)
        self.project = self.api_project.get()

    @staticmethod
    def to_html(text):
        """Convert the input text format to html.  A lot more could be done here."""
        return text.replace("\n", "<br/>")

    def add_label(self, external_id, name, color):
        existing = [label for label in self.project['labels'] if label['name'] == name]
        if existing:
            self.label_mapping[external_id] = existing[0]['id']
        else:
            new_label = self.api_project.labels.post({'name': name, 'color': color})
            self.project['labels'].append(new_label)
            self.label_mapping[external_id] = new_label['id']

    def set_cell_mapping(self, external_id, cell_name, identifiers=[]):
        """Set up a mapping from an external cell/column/list to a named cell in this project.
           Will look at full_label, and then label on cell to make a match
           Limitation: don't have multiple cells with the same full_label set, it'll default to the first one it finds.
           """
        if not self.board_cells:
            self.board_cells = self.api_project.boardcell.get()
            logger.info("Retrieved cell list")
        cells = [cell for cell in self.board_cells if cell['full_label'] == cell_name]
        if cells:
            if len(cells) > 1:
                logger.warn('Multiple cells found for %s, picking one' % cell_name)
            self.cell_mapping[external_id] = cells[0]['id']
            logger.info('Found cell for %s' % cell_name)
            return
        cells = [cell for cell in self.board_cells if cell['label'] == cell_name]
        if cells:
            if len(cells) > 1:
                logger.warn('Multiple cells found for %s, picking one' % cell_name)
            self.cell_mapping[external_id] = cells[0]['id']
            logger.info('Found cell for %s' % cell_name)
            return
        raise Exception(u'No cell found for %s' % cell_name)

    def set_cell(self, external_card_id, external_cell_id):
        cell_id = self.cell_mapping[external_cell_id]
        self.set_card_property(external_card_id, 'cell_id', cell_id)

    def set_iteration(self, iteration_id):
        if self.api_iteration is not None:
            raise Exception('ScrumDoImport can only import one iteration per instance.')
        self.api_iteration = self.api_project.iterations(iteration_id)

    def create_iteration(self, name):
        """Creates an iteration for the import, only do this once per import"""
        if self.api_iteration is not None:
            raise Exception('ScrumDoImport can only import one iteration per instance.')
        iteration = self.api_project.iterations.post({'name': name})
        iteration_id = iteration['id']
        self.api_iteration = self.api_project.iterations(iteration_id)

    def set_assignees(self, external_card_id, members):
        assignees = ", ".join([self.assignee_mapping.get(member, None) for member in members if self.assignee_mapping.get(member, None) is not None])
        missing_assignees = ", ".join([member for member in members if self.assignee_mapping.get(member, None) is None])
        if missing_assignees:
            logger.warn("Could not find assignees: %s" % missing_assignees)
        self.set_card_property(external_card_id, "assignees", assignees)

    def add_assignee_mapping(self, external_id, scrumdo_username):
        self.assignee_mapping[external_id] = scrumdo_username

    def add_card(self, external_card_id, card_properties):
        if external_card_id in self.card_properties:
            raise Exception('You called add_card with an id that already exists %s' % external_card_id)
        self.card_properties[external_card_id] = card_properties

    def set_card_property(self, external_card_id, property_name, value):
        """After you do an add_card, if you find out additional information about that card,
           you can call this to set those properties. """
        if not external_card_id in self.card_properties:
            raise Exception('Can not set card property on a card not yet added. %s' % external_card_id)
        self.card_properties[external_card_id][property_name] = value

    def _convert_label(self, label):
        return self.label_mapping[label]

    def set_labels(self, external_card_id, external_label_ids):
        """Takes an array of label id's from the source system, converts them, and
           adds them to a card."""
        labels = [{'id': self._convert_label(label)} for label in external_label_ids]
        self.set_card_property(external_card_id, 'labels', labels)

    def assign_card(self, external_card_id, external_assignee_id):
        self.assignees[external_card_id].append(external_assignee_id)

    def add_attachment_by_filename(self, external_card_id, filename):
        self.attachments[external_card_id].append(filename)

    def add_attachment_by_url(self, external_card_id, url, filename):
        if not os.path.exists("temp/attachments"):
            os.makedirs("temp/attachments")
        df = urllib2.urlopen(url)
        filename = u"temp/attachments/{filename}".format(filename=filename)
        with open(filename, 'wb') as output:
            output.write(df.read())
            output.close()
            self.attachments[external_card_id].append(filename)

    def add_comment(self, external_card_id, comment_date, comment_text, comment_author):
        """
        :param external_card_id: id of the card for this comment
        :param comment_date: Date comment was written, as a string: 2015-04-04T23:35:02
        :param comment_text: Text of comment
        :param comment_author:  external id of the person who wrote it
        :return:
        """
        self.comments[external_card_id].append({
            'date': comment_date,
            'comment': comment_text,
            'author': comment_author
        })

    def import_all(self):
        """After you have everything set up for the import, call this to actually write the data out to ScrumDo"""
        rank = 20000
        for external_id, properties in self.card_properties.iteritems():
            self._import_card(external_id, properties, rank)

    def _lookup_assignee(self, external_uid):
        a = self.assignees.get(external_uid, None)
        # if a is None:

        return a

    def _import_card(self, external_id, properties, rank):
        logger.debug('Importing card %s' % external_id)
        p = properties.copy()
        p['rank'] = rank

        assignees = [self._lookup_assignee(uid) for uid in self.assignees[external_id]]
        assignees = [assignee for assignee in assignees if assignee is not None]
        p['assignees'] = ", ".join(assignees)

        card = self.api_iteration.stories.post(p)
        card_id = card['id']