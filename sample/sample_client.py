# -*- coding: utf-8 -*-

"""
Example updates
"""

from mekk.rtm import RtmClient, create_and_authorize_connector_prompting_for_api_key

import logging
logging.basicConfig(level = logging.DEBUG)

APP_NAME = "mekk.rtm sample"

def run():
    connector = create_and_authorize_connector_prompting_for_api_key(
        APP_NAME, permission="delete")
    client = RtmClient(connector)

    ######################################################################
    # Lists
    ######################################################################

    print "Known lists: "
    for l in client.known_lists():
        print l

    print "Known smart lists: "
    for l in client.known_smart_lists():
        print l

    test_list = client.find_or_create_list(u"Zażółć gęślą jaźń")
    print "Test list: ", test_list

    test_list = client.archive_list(test_list.id)
    print "After archiving: ", test_list

    test_list = client.unarchive_list(test_list.id)
    print "After unarchiving: ", test_list

    ######################################################################
    # Tasks
    ######################################################################
    
    task = client.create_task(
        u"Bardzo poważne zadanie",
        list_id = test_list.id,
        tags = ["testy", "@dom"],
        priority = 3,
        due_date = "2010-11-30",
        estimate = "1 day 10 hours",
        repeat = "after 3 days",
        url = "http://www.google.com",
        completed = True,
        notes = [ (u"Brzęczy", u"mucha na pianinie\ni zupełnie nic nie ginie"),
                  (u"Strzela", u"krokodyl zielony\nbawi się z tej owej strony") ])
    print "Created task", task

    task2 = client.create_task(
        u"Zażółć gęślą jaźń")
    print "Created task", task2
    
    task2 = client.move_task(
        task2.key, test_list.id)
    print "Moved task", task2

    print "Tasks on test list"
    tlist_task = list(client.find_tasks(test_list.id))
    for t in tlist_task:
        print t

    print "All incomplete repeating tasks"
    for t in client.find_tasks(test_list.id, filter = "status:incomplete and isRepeating:true"):
        print t

    print "All tasks with notes"
    for t in client.find_tasks(test_list.id, filter = "status:incomplete and hasNotes:true"):
        print t

    ######################################################################
    # Cleanup
    ######################################################################

    # This won't work if token was acquired with permission=write, it needs
    # permission = delete

    for task in tlist_task:
        t = client.delete_task(task.key)
        print "Deleted task", t

    test_list = client.delete_list(test_list.id)
    print "Deleted list", test_list


if __name__ == "__main__":
    run()
