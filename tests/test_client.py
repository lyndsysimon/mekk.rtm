# -*- coding: utf-8 -*-

from mock import Mock, patch
from mekk.rtm.rtm_connector import RtmConnector
from mekk.rtm.rtm_client import RtmClient, List, SmartList, TaskKey, Task, Note
import httplib2
import nose.tools as nt
from nose import SkipTest
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import tzutc, tzlocal
import datetime

def assert_tasks_equal(task1, task2):
    for i1, i2 in zip(task1, task2):
        nt.assert_equal(i1,i2)
    nt.assert_equal(task1, task2)

def assert_tasklists_equal(tasklist1, tasklist2):
    nt.assert_equal(len(tasklist1), len(tasklist2))
    for t1, t2 in zip(tasklist1, tasklist2):
        assert_tasks_equal(t1, t2)

@patch.object(httplib2.Http, 'request')
def test_getLists(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","lists":{"list":[{"id":"5384544","name":"Inbox","deleted":"0","locked":"1","archived":"0","position":"-1","smart":"0","sort_order":"0"},{"id":"15938251","name":"Administracja","deleted":"0","locked":"0","archived":"0","position":"0","smart":"0","sort_order":"0"},{"id":"15958341","name":"Bez daty","deleted":"0","locked":"0","archived":"0","position":"0","smart":"1","sort_order":"0","filter":"(status:incomplete and due:never and NOT tag:maybe)"},{"id":"15938098","name":"Doko\u0144czenie laptopa","deleted":"0","locked":"0","archived":"0","position":"0","smart":"0","sort_order":"0"},{"id":"15938094","name":"Rodzina","deleted":"0","locked":"0","archived":"0","position":"0","smart":"0","sort_order":"0"},{"id":"15938246","name":"Praca","deleted":"0","locked":"0","archived":"0","position":"0","smart":"0","sort_order":"0"},{"id":"5384548","name":"Sent","deleted":"0","locked":"1","archived":"0","position":"1","smart":"0","sort_order":"0"}]}}}'
        )
    
    nt.assert_equal(client.known_lists(),
                    [List(id='15938246', name='Praca', archived=False), List(id='15938251', name='Administracja', archived=False), List(id='5384544', name='Inbox', archived=False), List(id='15938094', name='Rodzina', archived=False), List(id='15938098', name=u'Doko\u0144czenie laptopa', archived=False), List(id='5384548', name='Sent', archived=False)])

    nt.assert_equal(client.known_smart_lists(),
                    [SmartList(id='15958341', name='Bez daty', filter='(status:incomplete and due:never and NOT tag:maybe)', archived=False)])

    nt.assert_true(mock_req.called_once)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&method=rtm.lists.getList&api_sig=2ea15ec339e089945e32c6eacd7c3daa',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        #"getToken called with incorrect arguments"
        )

@patch.object(httplib2.Http, 'request')
def test_createTask(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532874891","undoable":"0"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:24Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
        )

    t = client.create_task(task_name = u"Bardzo poważne zadanie", list_id='16010288')

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, [])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, None)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.add&name=Bardzo+powa%C5%BCne+zadanie&timeline=337369522&api_sig=e46564058cc0fe306a6496be7a19f825',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )
    
@patch.object(httplib2.Http, 'request')
def test_addTags(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532874950","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:25Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           add_tags = ['testy', '@dom'])

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, None)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.addTags&tags=testy%2C+%40dom&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=be16a75471c3dd67ff164a7338b03b6e',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_addOneTag(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532874950","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:25Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":"@dom"},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           add_tags = ['@dom'])

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, None)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.addTags&tags=%40dom&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=24fd7a453c179406af257b8f01e38b62',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_complete(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875048","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:26Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"2010-11-09T20:25:26Z","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           completed = True)

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, None)
    nt.assert_equal(t.completed, dateutil_parse("2010-11-09T20:25:26Z"))
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.complete&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=dfea9679b4441be0172c7a17a641a22a',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_setPriority(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875068","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:27Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           priority=3)

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.setPriority&priority=3&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=82905c732a9719c70d33eeab70ee3b69',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_setDueDate(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875130","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:28Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"2010-11-30T00:00:00Z","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           due_date = datetime.date(2010,11,30))

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, datetime.datetime(2010,11,30, 0, 0, 0, tzinfo = tzutc()))
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&due=2010-11-30T00%3A00%3A00Z&format=json&list_id=16010288&method=rtm.tasks.setDueDate&parse=1&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=64592cad839829ef7c46dd1e35f0054e',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_setDueDateStr(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875130","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:28Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"2010-11-30T00:00:00Z","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           due_date = "2010-11-30")

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, datetime.datetime(2010,11,30, 0, 0, 0, tzinfo = tzutc()))
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&due=2010-11-30T00%3A00%3A00%2B00%3A00&format=json&list_id=16010288&method=rtm.tasks.setDueDate&parse=1&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=81d2b431eaa423828b94ee2a629a3c25',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_setDueDateLocalZone(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875130","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:28Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"2010-11-29T23:00:00Z","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":""}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           due_date = datetime.datetime(2010,11,30, tzinfo = tzlocal()))

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, datetime.datetime(2010,11,30, 0, 0, 0, tzinfo = tzlocal()))
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&due=2010-11-30T00%3A00%3A00%2B01%3A00&format=json&list_id=16010288&method=rtm.tasks.setDueDate&parse=1&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=1bdec40ebd6ca45fc1a3bd37bd9f4ee7',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )


@patch.object(httplib2.Http, 'request')
def test_setEstimate(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875179","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:29Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"2010-11-30T00:00:00Z","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           estimate = "1 day 10 hours")

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, datetime.datetime(2010,11,30, tzinfo=tzutc()))
    nt.assert_equal(t.estimate, "1 day 10 hours")
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&estimate=1+day+10+hours&format=json&list_id=16010288&method=rtm.tasks.setEstimate&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=ae22e8521e3bc2aecb32d1957803d5e3',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_setRecurrence(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875256","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:30Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           repeat = "after 3 days")

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, "1 day 10 hours")
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, "every FREQ=DAILY;INTERVAL=3")

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.setRecurrence&repeat=after+3+days&task_id=138637958&taskseries_id=92882408&timeline=337369522&api_sig=5c9b5176225f0b683a3e4ac0320779d4',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )


@patch.object(httplib2.Http, 'request')
def test_setURL(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2532875330","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:31Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"http:\/\/www.google.com","location_id":"","tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}}}}'
        )

    t = client.update_task(TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'),
                           url='http://www.google.com')

    nt.assert_equal(t.key, TaskKey(task_id='138637958', taskseries_id='92882408', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_equal(t.tags, ['@dom', 'testy'])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, "1 day 10 hours")
    nt.assert_equal(t.priority, 3)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)
    nt.assert_equal(t.url, 'http://www.google.com')

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.setURL&task_id=138637958&taskseries_id=92882408&timeline=337369522&url=http%3A%2F%2Fwww.google.com&api_sig=0e61a097428e47905b2d5d28af1acbe2',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_taskList(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        r'{"rsp":{"stat":"ok","tasks":{"rev":"s36piitmibkw8o8844os0sw0w8cwgcs","list":{"id":"16010288","taskseries":[{"id":"92141798","created":"2010-11-04T00:56:49Z","modified":"2010-11-04T00:56:49Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137446193","due":"","has_due_time":"0","added":"2010-11-04T00:56:49Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267415","created":"2010-11-05T00:12:37Z","modified":"2010-11-05T00:12:37Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137654081","due":"","has_due_time":"0","added":"2010-11-05T00:12:37Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267315","created":"2010-11-05T00:11:42Z","modified":"2010-11-05T00:11:42Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137653980","due":"","has_due_time":"0","added":"2010-11-05T00:11:42Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267038","created":"2010-11-05T00:08:53Z","modified":"2010-11-05T00:08:53Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137653635","due":"","has_due_time":"0","added":"2010-11-05T00:08:53Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92142890","created":"2010-11-04T01:12:40Z","modified":"2010-11-04T01:12:40Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137448202","due":"","has_due_time":"0","added":"2010-11-04T01:12:40Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92702791","created":"2010-11-08T18:28:50Z","modified":"2010-11-08T18:28:50Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"138378867","due":"","has_due_time":"0","added":"2010-11-08T18:28:50Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92577955","created":"2010-11-08T00:01:48Z","modified":"2010-11-08T00:01:48Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"138184879","due":"","has_due_time":"0","added":"2010-11-08T00:01:48Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92575473","created":"2010-11-07T23:32:16Z","modified":"2010-11-07T23:32:16Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"138180799","due":"","has_due_time":"0","added":"2010-11-07T23:32:16Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92386260","created":"2010-11-05T22:00:42Z","modified":"2010-11-05T22:00:42Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137843751","due":"","has_due_time":"0","added":"2010-11-05T22:00:42Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92386156","created":"2010-11-05T21:59:23Z","modified":"2010-11-05T21:59:23Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137843644","due":"","has_due_time":"0","added":"2010-11-05T21:59:23Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92386058","created":"2010-11-05T21:57:49Z","modified":"2010-11-05T21:57:49Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137843525","due":"","has_due_time":"0","added":"2010-11-05T21:57:49Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92384355","created":"2010-11-05T21:35:01Z","modified":"2010-11-05T21:35:01Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137841695","due":"","has_due_time":"0","added":"2010-11-05T21:35:01Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267862","created":"2010-11-05T00:16:34Z","modified":"2010-11-05T00:16:34Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137654583","due":"","has_due_time":"0","added":"2010-11-05T00:16:34Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267589","created":"2010-11-05T00:14:12Z","modified":"2010-11-05T00:14:12Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137654260","due":"","has_due_time":"0","added":"2010-11-05T00:14:12Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92267508","created":"2010-11-05T00:13:25Z","modified":"2010-11-05T00:13:25Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137654177","due":"","has_due_time":"0","added":"2010-11-05T00:13:25Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92882408","created":"2010-11-09T20:25:24Z","modified":"2010-11-09T20:25:31Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"http:\/\/www.google.com","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138637958","due":"2010-11-29T23:00:00Z","has_due_time":"0","added":"2010-11-09T20:25:24Z","completed":"2010-11-09T20:25:26Z","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92703754","created":"2010-11-08T18:35:56Z","modified":"2010-11-08T18:36:03Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"http:\/\/www.google.com","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138380362","due":"2010-11-29T23:00:00Z","has_due_time":"0","added":"2010-11-08T18:35:56Z","completed":"2010-11-08T18:35:58Z","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92703159","created":"2010-11-08T18:31:49Z","modified":"2010-11-08T18:31:55Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138379746","due":"2010-11-29T23:00:00Z","has_due_time":"0","added":"2010-11-08T18:31:49Z","completed":"2010-11-08T18:31:51Z","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92893307","created":"2010-11-09T21:58:53Z","modified":"2010-11-09T21:59:02Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"http:\/\/www.google.com","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17010299","created":"2010-11-09T21:59:02Z","modified":"2010-11-09T21:59:02Z","title":"Strzela","$t":"krokodyl zielony\nbawi si\u0119 z tej owej strony"},{"id":"17010298","created":"2010-11-09T21:59:01Z","modified":"2010-11-09T21:59:01Z","title":"Brz\u0119czy","$t":"mucha na pianinie\ni zupe\u0142nie nic nie ginie"}]},"task":{"id":"138650897","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-09T21:58:53Z","completed":"2010-11-09T21:58:55Z","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}]}}}}'
        )

    tsks = list(client.find_tasks('16010288'))

    for t in tsks:
        nt.assert_equal(t.key.list_id, '16010288')
        nt.assert_true(t.key.taskseries_id)
        nt.assert_true(t.key.task_id)
        nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
        nt.assert_true(type(t.tags) is list)
        nt.assert_true(type(t.notes) is list)
        nt.assert_true(all(tag in ['@dom', 'testy'] for tag in t.tags))
        for n in t.notes:
            nt.assert_true(n.id)
            nt.assert_true(n.title in ['Strzela', u"Brzęczy"])
            nt.assert_true(n.body in [ u"mucha na pianinie\ni zupełnie nic nie ginie",
                                       u"krokodyl zielony\nbawi się z tej owej strony" ])
        nt.assert_true(t.due in [None, 
                                 datetime.datetime(2010,11,30,0,0,0,tzinfo=tzutc()),
                                 datetime.datetime(2010,11,30,0,0,0,tzinfo=tzlocal()),
                                 ])
        nt.assert_true(t.estimate in [None, "1 day 10 hours"])
        nt.assert_true(t.priority in [None, 3])
        nt.assert_true(t.completed is None
                       or ((type(t.completed) is datetime.datetime)
                           and (t.completed > datetime.datetime(2010, 11, 8, tzinfo=tzutc()))
                           and (t.completed < datetime.datetime(2010, 11, 10, tzinfo=tzutc()))),
                       "Invalid completed: %s" % str(t.completed))
        nt.assert_equal(t.postponed, 0)
        nt.assert_true(t.repeat in [None, 'every FREQ=DAILY;INTERVAL=3'])
        nt.assert_true(t.url in [None, 'http://www.google.com'])

    nt.assert_true(any(t.tags for t in tsks))
    nt.assert_true(any(t.notes for t in tsks))
    nt.assert_true(any(t.due for t in tsks))
    nt.assert_true(any(t.estimate for t in tsks))
    nt.assert_true(any(t.repeat for t in tsks))
    nt.assert_true(any(t.url for t in tsks))
    nt.assert_true(any(t.priority for t in tsks))

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.getList&api_sig=e942c3574121c46613399e84956cbd86',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_taskListWithEmptyResult(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        r'{"rsp":{"stat":"ok","tasks":{"rev":"571qzwm6yl8gwko04c04oggkw8wgk44"}}}',
        )

    tsks = list(
        client.find_tasks('16010288',
                          filter = "status:incomplete and isRepeating:true"))
    nt.assert_equal(tsks, [])

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&filter=status%3Aincomplete+and+isRepeating%3Atrue&format=json&list_id=16010288&method=rtm.tasks.getList&api_sig=22e7fa4980893e7ac1f8e4ff582b31ab',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_taskListSmall(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        r'{"rsp":{"stat":"ok","tasks":{"rev":"coe3rd0gvy0wwk4484so0o8ck0ogw0c","list":{"id":"16097855","taskseries":{"id":"92957843","created":"2010-11-10T11:22:44Z","modified":"2010-11-10T11:22:52Z","name":"Write some unit tests","source":"api","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17032129","created":"2010-11-10T11:22:52Z","modified":"2010-11-10T11:22:52Z","title":"Helper","$t":"And mock can help to wrap backend apis\nwithout calling them"},{"id":"17032125","created":"2010-11-10T11:22:51Z","modified":"2010-11-10T11:22:51Z","title":"Runner","$t":"Use nose to run them all\nIt is simplest"}]},"task":{"id":"138767354","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:22:44Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}}}}}'
        )

    tsks = list(
        client.find_tasks('16097855',
                          filter = "status:incomplete and hasNotes:true"))
    nt.assert_equal(
        tsks, 
        [
            Task(key=TaskKey(list_id='16097855', task_id='138767354', taskseries_id='92957843'),
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[Note(id='17032129', title='Helper',
                             body='And mock can help to wrap backend apis\nwithout calling them'),
                        Note(id='17032125', title='Runner',
                             body='Use nose to run them all\nIt is simplest')],
                 due=datetime.datetime(2010, 11, 29, 23, 0, tzinfo=tzutc()),
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'),
            ]
        )

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&filter=status%3Aincomplete+and+hasNotes%3Atrue&format=json&list_id=16097855&method=rtm.tasks.getList&api_sig=620e46a1ca0c992fcafc6571b74d0297',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )

@patch.object(httplib2.Http, 'request')
def test_taskListMultiList(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        r'{"rsp":{"stat":"ok","tasks":{"rev":"otar2d6hpyoo8g8ggwc0kscowco008w","list":[{"id":"16097855","taskseries":[{"id":"92961841","created":"2010-11-10T12:06:33Z","modified":"2010-11-10T12:06:34Z","name":"Less serious one","source":"api","url":"","location_id":"","tags":{"tag":"testy"},"participants":[],"notes":[],"task":{"id":"138772685","due":"","has_due_time":"0","added":"2010-11-10T12:06:33Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92962722","created":"2010-11-10T12:15:26Z","modified":"2010-11-10T12:15:27Z","name":"Less serious one","source":"api","url":"","location_id":"","tags":{"tag":"testy"},"participants":[],"notes":[],"task":{"id":"138773641","due":"","has_due_time":"0","added":"2010-11-10T12:15:26Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}},{"id":"92957843","created":"2010-11-10T11:22:44Z","modified":"2010-11-10T11:22:52Z","name":"Write some unit tests","source":"api","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17032129","created":"2010-11-10T11:22:52Z","modified":"2010-11-10T11:22:52Z","title":"Helper","$t":"And mock can help to wrap backend apis\nwithout calling them"},{"id":"17032125","created":"2010-11-10T11:22:51Z","modified":"2010-11-10T11:22:51Z","title":"Runner","$t":"Use nose to run them all\nIt is simplest"}]},"task":{"id":"138767354","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:22:44Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92962705","created":"2010-11-10T12:15:16Z","modified":"2010-11-10T12:15:24Z","name":"Write some unit tests","source":"api","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17034235","created":"2010-11-10T12:15:24Z","modified":"2010-11-10T12:15:24Z","title":"Helper","$t":"And mock can help to wrap backend apis\nwithout calling them"},{"id":"17034234","created":"2010-11-10T12:15:23Z","modified":"2010-11-10T12:15:23Z","title":"Runner","$t":"Use nose to run them all\nIt is simplest"}]},"task":{"id":"138773623","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T12:15:16Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92961825","created":"2010-11-10T12:06:23Z","modified":"2010-11-10T12:06:31Z","name":"Write some unit tests","source":"api","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17034064","created":"2010-11-10T12:06:31Z","modified":"2010-11-10T12:06:31Z","title":"Helper","$t":"And mock can help to wrap backend apis\nwithout calling them"},{"id":"17034063","created":"2010-11-10T12:06:30Z","modified":"2010-11-10T12:06:30Z","title":"Runner","$t":"Use nose to run them all\nIt is simplest"}]},"task":{"id":"138772666","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T12:06:23Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92958016","created":"2010-11-10T11:25:05Z","modified":"2010-11-10T11:25:05Z","name":"Write some unit tests","source":"js","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138767536","due":"2010-11-12T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:25:05Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92957923","created":"2010-11-10T11:23:55Z","modified":"2010-11-10T11:23:55Z","name":"Write some unit tests","source":"js","url":"http:\/\/en.wikipedia.org\/wiki\/Unit_testing","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138767436","due":"2010-11-12T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:23:55Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}]},{"id":"16010288","taskseries":[{"id":"92957172","created":"2010-11-10T11:14:29Z","modified":"2010-11-10T11:14:37Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"http:\/\/www.google.com","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":{"note":[{"id":"17031416","created":"2010-11-10T11:14:37Z","modified":"2010-11-10T11:14:37Z","title":"Strzela","$t":"krokodyl zielony\nbawi si\u0119 z tej owej strony"},{"id":"17031414","created":"2010-11-10T11:14:36Z","modified":"2010-11-10T11:14:36Z","title":"Brz\u0119czy","$t":"mucha na pianinie\ni zupe\u0142nie nic nie ginie"}]},"task":{"id":"138766629","due":"2010-11-29T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:14:29Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}},{"id":"92957207","created":"2010-11-10T11:15:08Z","modified":"2010-11-10T11:15:08Z","name":"Bardzo powa\u017cne zadanie","source":"js","url":"http:\/\/www.google.com","location_id":"","rrule":{"every":"0","$t":"FREQ=DAILY;INTERVAL=3"},"tags":{"tag":["@dom","testy"]},"participants":[],"notes":[],"task":{"id":"138766685","due":"2010-11-12T23:00:00Z","has_due_time":"1","added":"2010-11-10T11:15:08Z","completed":"","deleted":"","priority":"3","postponed":"0","estimate":"1 day 10 hours"}}]}]}}}'
        )

    tsks = list(
        client.find_tasks(filter = "tag:testy and status:incomplete"))
    assert_tasklists_equal(
        tsks,
        [
            Task(key=TaskKey(list_id='16097855', task_id='138772685', taskseries_id='92961841'),
                 name='Less serious one',
                 tags=['testy'], 
                 notes=[],
                 due=None,
                 estimate=None,
                 priority=None,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat=None,
                 url=None),
            Task(key=TaskKey(list_id='16097855', task_id='138773641', taskseries_id='92962722'),
                 name='Less serious one', 
                 tags=['testy'], 
                 notes=[], 
                 due=None, 
                 estimate=None, 
                 priority=None, 
                 completed=None, 
                 deleted=None,
                 postponed=0, 
                 repeat=None, 
                 url=None),
            Task(key=TaskKey(list_id='16097855', task_id='138767354', taskseries_id='92957843'),
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[Note(id='17032129', title='Helper',
                             body='And mock can help to wrap backend apis\nwithout calling them'),
                        Note(id='17032125', title='Runner',
                             body='Use nose to run them all\nIt is simplest')], 
                 due=datetime.datetime(2010, 11, 29, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'),
            Task(key=TaskKey(list_id='16097855', task_id='138773623', taskseries_id='92962705'),
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[Note(id='17034235', title='Helper',
                             body='And mock can help to wrap backend apis\nwithout calling them'),
                        Note(id='17034234', title='Runner',
                             body='Use nose to run them all\nIt is simplest')],
                 due=datetime.datetime(2010, 11, 29, 23, 0, tzinfo=tzutc()),
                 estimate='1 day 10 hours', 
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'),
            Task(key=TaskKey(list_id='16097855', task_id='138772666', taskseries_id='92961825'),
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[Note(id='17034064', title='Helper',
                             body='And mock can help to wrap backend apis\nwithout calling them'), 
                        Note(id='17034063', title='Runner',
                             body='Use nose to run them all\nIt is simplest')],
                 due=datetime.datetime(2010, 11, 29, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours', 
                 priority=3, 
                 completed=None, 
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'),
            Task(key=TaskKey(list_id='16097855', task_id='138767536', taskseries_id='92958016'), 
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[],
                 due=datetime.datetime(2010, 11, 12, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0, 
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'), 
            Task(key=TaskKey(list_id='16097855', task_id='138767436', taskseries_id='92957923'), 
                 name='Write some unit tests',
                 tags=['@dom', 'testy'],
                 notes=[],
                 due=datetime.datetime(2010, 11, 12, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://en.wikipedia.org/wiki/Unit_testing'), 
            Task(key=TaskKey(list_id='16010288', task_id='138766629', taskseries_id='92957172'), 
                 name=u'Bardzo powa\u017cne zadanie',
                 tags=['@dom', 'testy'],
                 notes=[Note(id='17031416', title='Strzela',
                             body=u'krokodyl zielony\nbawi si\u0119 z tej owej strony'),
                        Note(id='17031414', title=u'Brz\u0119czy',
                             body=u'mucha na pianinie\ni zupe\u0142nie nic nie ginie')],
                 due=datetime.datetime(2010, 11, 29, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://www.google.com'), 
            Task(key=TaskKey(list_id='16010288', task_id='138766685', taskseries_id='92957207'), 
                 name=u'Bardzo powa\u017cne zadanie',
                 tags=['@dom', 'testy'],
                 notes=[],
                 due=datetime.datetime(2010, 11, 12, 23, 0, tzinfo=tzutc()), 
                 estimate='1 day 10 hours',
                 priority=3,
                 completed=None,
                 deleted=None,
                 postponed=0,
                 repeat='every FREQ=DAILY;INTERVAL=3',
                 url='http://www.google.com')
            ])

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&filter=tag%3Atesty+and+status%3Aincomplete&format=json&method=rtm.tasks.getList&api_sig=2da12cfd87ef0742e7733c25a4a2f1f8',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )


@patch.object(httplib2.Http, 'request')
def test_deleteTask(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","transaction":{"id":"2536870899","undoable":"1"},"list":{"id":"16010288","taskseries":{"id":"92141798","created":"2010-11-04T00:56:49Z","modified":"2010-11-10T14:44:43Z","name":"Bardzo powa\u017cne zadanie","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"137446193","due":"","has_due_time":"0","added":"2010-11-04T00:56:49Z","completed":"","deleted":"2010-11-10T14:44:43Z","priority":"N","postponed":"0","estimate":""}}}}}'
        )

    t = client.delete_task(TaskKey(task_id='137446193', taskseries_id='92141798', list_id='16010288'))

    nt.assert_equal(t.key, TaskKey(task_id='137446193', taskseries_id='92141798', list_id='16010288'))
    nt.assert_equal(t.name,  u"Bardzo poważne zadanie")
    nt.assert_true(t.deleted)
    nt.assert_true(type(t.deleted) is datetime.datetime)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&list_id=16010288&method=rtm.tasks.delete&task_id=137446193&taskseries_id=92141798&timeline=337369522&api_sig=f0a258eca99ead360d96e5167128b0f1',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )


    
@patch.object(httplib2.Http, 'request')
def test_addNotes(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    raise SkipTest

@patch.object(httplib2.Http, 'request')
def test_moveTask(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    client  = RtmClient(connector)
    client._timeline = '337369522'

    mock_req.return_value = (
        dict(status='200'),
        r"""
{"rsp":{"stat":"ok","transaction":{"id":"2554995402","undoable":"1"},"list":{"id":"16150681","taskseries":{"id":"93467164","created":"2010-11-14T10:53:04Z","modified":"2010-11-14T10:53:05Z","name":"Za\u017c\u00f3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144","source":"api","url":"","location_id":"","tags":[],"participants":[],"notes":[],"task":{"id":"139580828","due":"","has_due_time":"0","added":"2010-11-14T10:53:04Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}}}
""")
    old_id = TaskKey(
        task_id='139580828', taskseries_id='93467164', list_id='5384544')
    new_id = TaskKey(
        task_id='139580828', taskseries_id='93467164', list_id='16150681')
    t = client.move_task(
        old_id,
        new_list_id = new_id.list_id)

    nt.assert_equal(t.key, new_id)
    nt.assert_equal(t.name,  u"Zażółć gęślą jaźń")
    nt.assert_equal(t.tags, [])
    nt.assert_equal(t.notes, [])
    nt.assert_equal(t.due, None)
    nt.assert_equal(t.estimate, None)
    nt.assert_equal(t.priority, None)
    nt.assert_equal(t.completed, None)
    nt.assert_equal(t.deleted, None)
    nt.assert_equal(t.postponed, 0)
    nt.assert_equal(t.repeat, None)

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&from_list_id=5384544&method=rtm.tasks.moveTo&task_id=139580828&taskseries_id=93467164&timeline=337369522&to_list_id=16150681&api_sig=cff6742ae43d75d4079bd28484fff27b',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        )
