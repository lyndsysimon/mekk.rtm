# -*- coding: utf-8 -*-

"""
Tests related to the public commands
"""

from mekk.rtm.helpers.run_tag import modify_tags

from mock import Mock, patch
from mekk.rtm.rtm_connector import RtmConnector
from mekk.rtm.rtm_client import RtmClient, List, SmartList, TaskKey, Task, Note
import httplib2
import nose.tools as nt
from nose import SkipTest
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import tzutc, tzlocal
import datetime
import re

def tagger_generate_reply(url, headers):
    """
    Helper method for mocking tag testing.
    """
    if "&method=rtm.tasks.getList&" in url:
        return (
            dict(status='200'),
            r'{"rsp":{"stat":"ok","tasks":{"rev":"coe3rd0gvy0wwk4484so0o8ck0ogw0c","list":{"id":"16097855","taskseries":[{"id":"92957843","created":"2010-11-10T11:22:44Z","modified":"2010-11-10T11:22:52Z","name":"Write some unit tests","source":"api","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17032129","created":"2010-11-10T11:22:52Z","modified":"2010-11-10T11:22:52Z","title":"Helper","$t":"And mock can help to wrap backend apis\nwithout calling them"},{"id":"17032125","created":"2010-11-10T11:22:51Z","modified":"2010-11-10T11:22:51Z","title":"Runner","$t":"Use nose to run them all\nIt is simplest"}]},"task":{"id":"138767354","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:22:44Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92141798","created":"2010-11-04T00:56:49Z","modified":"2010-11-04T00:56:49Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","krokodyl"]},"participants":[],"notes":[],"task":{"id":"137446193","due":"","has_due_time":"0","added":"2010-11-04T00:56:49Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267415","created":"2010-11-05T00:12:37Z","modified":"2010-11-05T00:12:37Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137654081","due":"","has_due_time":"0","added":"2010-11-05T00:12:37Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}]}}}}'
                )
    elif "&method=rtm.timelines.create&" in url:
        return (
            dict(status='200'),
            r'{"rsp":{"stat":"ok","timeline":"12345"}}'
            )
    elif "&method=rtm.tasks.setTags&" in url:
        return (
            dict(status='200'),
            r'{"rsp":{"stat":"ok","transaction":{"id":"2532874950","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:25Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
            )
    else:
        raise Exception("Unexpected url: " + url)

@patch.object(httplib2.Http, 'request')
def test_addTags(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.side_effect = tagger_generate_reply

    modify_tags(client, filter = u'status:incomplete and inlist:Test', 
                add_tags = ['@dom', 'testy'],
                remove_tags = [])

    # Były trzy zadania ale jedno już ma te tagi. Do tego timeline i getlist
    nt.assert_equal(mock_req.call_count, 4)

    called_urls = [x[0][0] for x in mock_req.call_args_list]

    nt.assert_true('&method=rtm.tasks.getList&' in called_urls[0])
    nt.assert_true('&method=rtm.timelines.create&' in called_urls[1])

    nt.assert_equal(called_urls[2], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=%40dom%2Ckrokodyl%2Ctesty&task_id=137446193&taskseries_id=92141798&timeline=12345&api_sig=9eb1901dbc1a51a8099590d757aa879f')
    nt.assert_equal(called_urls[3], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=%40dom%2Ctesty&task_id=137654081&taskseries_id=92267415&timeline=12345&api_sig=55cadb2d449bb90128b59b4ed5f8776d')

@patch.object(httplib2.Http, 'request')
def test_removeTags(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.side_effect = tagger_generate_reply

    modify_tags(client, filter = u'status:incomplete and inlist:Test', 
                remove_tags = ['@dom', 'krokodyl'])

    # Były trzy zadania ale jedno bez tych . Do tego timeline i getlist
    nt.assert_equal(mock_req.call_count, 4)

    called_urls = [x[0][0] for x in mock_req.call_args_list]

    nt.assert_true('&method=rtm.tasks.getList&' in called_urls[0])
    nt.assert_true('&method=rtm.timelines.create&' in called_urls[1])

    nt.assert_equal(called_urls[2], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=testy&task_id=138767354&taskseries_id=92957843&timeline=12345&api_sig=137768b0489acf13f17a353f4fcf2894')
    nt.assert_equal(called_urls[3], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=&task_id=137446193&taskseries_id=92141798&timeline=12345&api_sig=7f59d878f9da0562c0fd024d4e8229ff')

@patch.object(httplib2.Http, 'request')
def test_addRemoveTags(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.side_effect = tagger_generate_reply

    modify_tags(client, filter = u'status:incomplete and inlist:Test',
                add_tags = ['testy'],
                remove_tags = ['@dom', 'krokodyl'])

    nt.assert_equal(mock_req.call_count, 5)

    called_urls = [x[0][0] for x in mock_req.call_args_list]

    nt.assert_true('&method=rtm.tasks.getList&' in called_urls[0])
    nt.assert_true('&method=rtm.timelines.create&' in called_urls[1])

    nt.assert_equal(called_urls[2], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=testy&task_id=138767354&taskseries_id=92957843&timeline=12345&api_sig=137768b0489acf13f17a353f4fcf2894')
    nt.assert_equal(called_urls[3], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=testy&task_id=137446193&taskseries_id=92141798&timeline=12345&api_sig=36884dadc39306b7a7e07a2b5bfe3f3c')
    nt.assert_equal(called_urls[4], 'http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16097855&method=rtm.tasks.setTags&tags=testy&task_id=137654081&taskseries_id=92267415&timeline=12345&api_sig=778dc222b9f9badec7b4b68e643a9497')

@patch.object(httplib2.Http, 'request')
def test_addTagsDryRun(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.side_effect = tagger_generate_reply

    modify_tags(client, filter = u'status:incomplete and inlist:Test',
                add_tags = ['testy'],
                remove_tags = ['@dom', 'krokodyl'],
                dry_run = True)

    nt.assert_equal(mock_req.call_count, 1)

    called_urls = [x[0][0] for x in mock_req.call_args_list]

    nt.assert_true('&method=rtm.tasks.getList&' in called_urls[0])

def tagger_alt_generate_reply(url, headers):
    """
    Helper method for mocking tag testing (alternative tasks)
    """
    if "&method=rtm.tasks.getList&" in url:
        return (            
            dict(status='200'),
            r'{"rsp":{"stat":"ok","tasks":{"rev":"pzd6wt1m928kwoggk00o404ggs8sc84","list":{"id":"15938269","taskseries":[{"id":"91504390","created":"2010-10-29T18:08:12Z","modified":"2010-10-31T15:14:37Z","name":"Wzi\u0105\u0107 leki","source":"api","url":"","location_id":"","tags":{"tag":"@@next"},"participants":[],"notes":[],"task":{"id":"136365343","due":"","has_due_time":"0","added":"2010-10-29T18:08:12Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"91504394","created":"2010-10-29T18:08:14Z","modified":"2010-10-30T23:53:08Z","name":"Rozpisa\u0107 imprezy","source":"api","url":"","location_id":"","tags":{"tag":"@komputer"},"participants":[],"notes":[],"task":{"id":"136365348","due":"","has_due_time":"0","added":"2010-10-29T18:08:14Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":"15 minutes"}},{"id":"91504399","created":"2010-10-29T18:08:17Z","modified":"2010-10-31T20:11:46Z","name":"Zeszyty dla dzieci","source":"api","url":"","location_id":"","tags":{"tag":["greg","jane","komputer"]},"participants":[],"notes":[],"task":{"id":"136365354","due":"2011-02-17T23:00:00Z","has_due_time":"1","added":"2010-10-29T18:08:17Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"91504413","created":"2010-10-29T18:08:27Z","modified":"2010-10-31T20:11:28Z","name":"Wycieczka do Z","source":"api","url":"","location_id":"","rrule":{"every":"1","$t":"FREQ=YEARLY;INTERVAL=1"},"tags":{"tag":["mm","prezenty","zakupy"]},"participants":[],"notes":[],"task":{"id":"136365370","due":"2011-02-01T23:00:00Z","has_due_time":"1","added":"2010-10-29T18:08:27Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"91504417","created":"2010-10-29T18:08:31Z","modified":"2010-10-31T16:23:04Z","name":"Wizyta u ortodonty","source":"api","url":"","location_id":"732982","tags":{"tag":["jane","lekarz"]},"participants":[],"notes":[],"task":{"id":"136365375","due":"2010-12-03T08:40:00Z","has_due_time":"1","added":"2010-10-29T18:08:31Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":"60 minutes"}},{"id":"91504385","created":"2010-10-29T18:08:08Z","modified":"2010-11-12T23:06:55Z","name":"Basen (MSP) raz w tygodniu","source":"api","url":"","location_id":"","rrule":{"every":"1","$t":"FREQ=WEEKLY;INTERVAL=1;BYDAY=SA"},"tags":{"tag":"jane"},"participants":[],"notes":[],"task":[{"id":"139306587","due":"2010-11-19T23:00:00Z","has_due_time":"1","added":"2010-11-12T23:06:55Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""},{"id":"137856490","due":"2010-11-12T23:00:00Z","has_due_time":"1","added":"2010-11-05T23:05:46Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}]}]}}}}')
    elif "&method=rtm.timelines.create&" in url:
        return (
            dict(status='200'),
            r'{"rsp":{"stat":"ok","timeline":"12345"}}'
            )
    elif "&method=rtm.tasks.setTags&" in url:
        return (
            dict(status='200'),
            r'{"rsp":{"stat":"ok","transaction":{"id":"2532874950","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:25Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
            )
    else:
        raise Exception("Unexpected url: " + url)

@patch.object(httplib2.Http, 'request')
def test_addTagsToSingle(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.side_effect = tagger_alt_generate_reply

    modify_tags(client, filter = u'list:"Rodzina" and status:"incomplete"',
                add_tags = ['rodzina'])

    nt.assert_equal(mock_req.call_count, 9)

    called_urls = [x[0][0] for x in mock_req.call_args_list]

    nt.assert_true('&method=rtm.tasks.getList&' in called_urls[0])
    nt.assert_true('&method=rtm.timelines.create&' in called_urls[1])

    nt.assert_true(all('&method=rtm.tasks.setTags&' in x for x in called_urls[2:]))

    r_tags = re.compile('&tags=([^&]*)&')
    tags = [ r_tags.search(x).group(1) for x in called_urls[2:] ]

    from urllib import urlencode

    nt.assert_equal(tags[0], '%40%40next%2Crodzina')
    nt.assert_equal("tags="+tags[1],
                    urlencode(dict(tags='@komputer,rodzina')))
    nt.assert_equal("tags="+tags[2],
                    urlencode(dict(tags='greg,jane,komputer,rodzina')))
    nt.assert_equal("tags="+tags[3],
                    urlencode(dict(tags='mm,prezenty,rodzina,zakupy')))
    nt.assert_equal("tags="+tags[4],
                    urlencode(dict(tags='jane,lekarz,rodzina')))
    nt.assert_equal("tags="+tags[5],
                    urlencode(dict(tags='jane,rodzina')))
    nt.assert_equal("tags="+tags[6],
                    urlencode(dict(tags='jane,rodzina')))
