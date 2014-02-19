# -*- coding: utf-8 -*-
# Example referenced in README.txt

import logging
logging.basicConfig(level = logging.DEBUG)

# Workaround UnicodeEncodeError: 'ascii' codec can't encode characters if piping through less
import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from mekk.rtm import RtmClient, RtmConnector, create_and_authorize_connector_prompting_for_api_key

APP_NAME = "mekk.rtm sample"

connector = create_and_authorize_connector_prompting_for_api_key(APP_NAME)
#
# Function above interactively prompts for api key and shared secret and
# preserves acquired data in keyring. This is useful for testing, but in
# normal case you are more likely to do:
#
#    connector = create_and_authorize_connector(APP_NAME, API_KEY, SHARED_SECRET)

client = RtmClient(connector)

print "Normal lists: "
for l in client.known_lists():
    if not l.archived:
        print u"%s (%s)" % (l.id, l.name)

print "smart lists: "
for l in client.known_smart_lists():
    if not l.archived:
        print u"%s (%s, %s)" % (l.id, l.name, l.filter)

test_list = client.find_or_create_list(u"The testing list")
print "Test list: ", test_list

another_list = client.find_or_create_list(u"The testing list")
print "Another list: ", another_list

task1 = client.create_task(
    u"Write some unit tests",
    list_id = test_list.id,
    tags = ["testy", "@dom"],
    priority = 3,
    due_date = "2010-11-30",
    estimate = "1 day 10 hours",
    repeat = "after 3 days",
    url = "http://en.wikipedia.org/wiki/Unit_testing",
    completed = False,
    notes = [ (u"Runner", u"Use nose to run them all\nIt is simplest"),
              (u"Helper", u"And mock can help to wrap backend apis\nwithout calling them") ])
print "Created task", task1

task2 = client.create_task(
    u"Less serious one",
    list_id = test_list.id)
print "Created task", task2

task3 = client.create_task(
    u"Less serious one",
    list_id = another_list.id,
    tags = ["testy"])
print "Created task", task3

print "All incomplete tasks with notes on first list:"
for t in client.find_tasks(list_id = test_list.id, filter = "status:incomplete and hasNotes:true"):
    print t

task2 = client.update_task(
    task2.key,
    completed = True)
print "Updated task", task2

print "All incomplete tasks tagged 'testy':"
for t in client.find_tasks(filter = "tag:testy and status:incomplete"):
    print t


