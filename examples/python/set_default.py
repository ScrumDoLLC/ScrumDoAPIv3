#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slumber
from colorama import init, Fore, Back, Style
from time import sleep
import local_settings as settings
import json
# We're using slumber (http://slumber.in/), a python library that makes RESTfull calls amazingly easy to access the API

DEFAULT_VALUES = {
	'extra_1': u"<p><b><u>CODE:</u></b></p><p>Locally Tested - </p><p>Remotely Tested(separate team member) - </p><p>Syntax adheres to Team Standard -</p><p>Committed to VCS(development branch) - </p><p>Desgin of output matches Company Standard look and feel - </p><p><b><u>SCRUM CARD:</u></b></p><p>In Ready to Review(QA) - </p><p>All tasks completed - </p><p>Effort logged on all tasks - </p><p>Comments made against work - </p><p>Attached files(code/scripts/sql) - </p><p>Tagged &#34;PushToLive&#34; if ready for production - </p>"
}

def main():
	init()
	base_url = "%s/openapi/v3/" % settings.scrumdo_host
	api = slumber.API(base_url, auth=(settings.scrumdo_username, settings.scrumdo_password))
	set_defaults(api)

def set_defaults(api):
	page = 1
	try:
		# First, let's make sure we have a valid org / project, this call will return a 403 and throw an exception if not
		project = api.organizations(settings.organization_slug).projects(settings.project_slug).get()
		# print "Project info: %s" % json.dumps(project, sort_keys=True, indent=4) # slumber converts JSON to python dicts for us, but to print it pretty, out lets output json

		finished = False
		while not finished:
			stories = api.organizations(settings.organization_slug).projects(settings.project_slug).stories.get(page=page)
			page += 1
			print "Page %d / %d" % (stories['current_page'], stories['max_page'])
			finished = stories['current_page'] == stories['max_page']
			for story in stories['items']:
				if story['extra_1'] == '':
					api.organizations(settings.organization_slug).projects(settings.project_slug).stories(story['id']).put(DEFAULT_VALUES)
					print "Updated story #%d" % story['number']

	except slumber.exceptions.HttpServerError as e:
		print e
		print e.content


if __name__ == "__main__":
    main()
