# Had a customer lose labels from his cards
# This script looks at a version of ScrumDo running a restored older version of the database and
# compares it to the current production scrumdo, and copies over the label info.
#
# Was also concerned about tags, so this verifies none changed.

import slumber
import local_settings as settings
import json

import slumber
from colorama import init, Fore, Back, Style
from time import sleep
import local_settings as settings
import json

def main():
    init()
    base_url = "%s/api/v3/" % settings.scrumdo_host
    api = slumber.API(base_url, auth=(settings.scrumdo_username, settings.scrumdo_password))

    base_url = "%s/api/v3/" % settings.backup_scrumdo_host
    api_backup = slumber.API(base_url, auth=(settings.scrumdo_username, settings.scrumdo_password))

    fix_all_labels(api, api_backup)

def verify_tags(api, story):
    try:
        new_story = api.organizations(settings.organization_slug).projects(settings.project_slug).stories(story['id']).get()
    except:
        print "Could not check %d" % story['id']
        return
    if new_story['tags'] != story['tags']:
        print "Story #%d had different tags %s / %s" % (story['number'], story['tags'], new_story['tags'])

def fix_label_for_story(api, story, available_labels):
    newLabels = []
    for oldLabel in story['labels']:
        # Due to the nature of this problem, we want to find the label by it's name and not it's ID
        newLabel = next( (label for label in available_labels if label['name']==oldLabel['name']), None)
        if newLabel:
            newLabels.append(newLabel)
        else:
            print "COULD NOT FIND %s" % oldLabel['name']

    print "Setting story #%d to %s" % (story['id'], ",".join(map(lambda l: l['name'], newLabels)))
    if len(newLabels) == 0:
        return
    try:
        api.organizations(settings.organization_slug).projects(settings.project_slug).stories(story['id']).put({'labels':newLabels})
    except:
        print "FAILED"


def fix_all_labels(api, api_backup):
    page = 1
    try:
        # First, let's grab the list of available labels.
        project = api.organizations(settings.organization_slug).projects(settings.project_slug).get()
        labels = project['labels']

        finished = False
        while not finished:
            stories = api_backup.organizations(settings.organization_slug).projects(settings.project_slug).stories.get(page=page)
            page += 1
            print "Page %d / %d" % (stories['current_page'], stories['max_page'])
            finished = stories['current_page'] == stories['max_page']
            for story in stories['items']:
                fix_label_for_story(api, story, labels)
                verify_tags(api, story)

    except slumber.exceptions.HttpServerError as e:
        print e
        print e.content


if __name__ == "__main__":
    main()
