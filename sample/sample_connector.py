# -*- coding: utf-8 -*-

"""
Example for low-level API (pure connector)
"""

from mekk.rtm import RtmConnector, create_and_authorize_connector_prompting_for_api_key
import logging

logging.basicConfig(level = logging.DEBUG)

APP_NAME = "mekk.rtm lowlevel sample"

def run():
    connector = create_and_authorize_connector_prompting_for_api_key(APP_NAME)

    print connector.call("rtm.test.login")

    print connector.call("rtm.tasks.getList", filter="status:incomplete and dueBefore:today and tag:platon")

    r = connector.call("rtm.timelines.create")
    print r
    tline = r['timeline']

    r = connector.call("rtm.tasks.add", timeline=tline, name=u"Zażółć gęślą jaźń", list_id = None)
    task_key = dict(
        list_id = r['list']['id'],
        taskseries_id = r['list']['taskseries']['id'],
        task_id = r['list']['taskseries']['task']['id'])
    print r

    print connector.call("rtm.tasks.notes.add", 
                         timeline=tline, note_title=u"Żółta karteczka",
                         note_text=u"Ciekawy pasjonujący tekst\no wampirach",
                         **task_key)

    #print connector.call("rtm.lists.getList")

if __name__ == "__main__":
    run()
