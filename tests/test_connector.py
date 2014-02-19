# -*- coding: utf-8 -*-

from mock import Mock, patch
from mekk.rtm.rtm_connector import RtmConnector
import httplib2
import nose.tools as nt
from nose import SkipTest

def assert_structs_equal(s1, s2):
    nt.assert_equal(type(s1), type(s2))
    if type(s1) is list:
        nt.assert_equal(len(s1), len(s2))
        for idx in range(0, len(s1)):
            assert_structs_equal(s1[idx], s2[idx])
    elif type(s1) is dict:
        nt.assert_equal(sorted(s1.keys()), sorted(s2.keys()))
        for key in s1:
            assert_structs_equal(s1[key], s2[key])
    else:
        nt.assert_equal(s1, s2)
        
        

@patch.object(httplib2.Http, 'request')
def test_connectionWithTokenAcquisition(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", None)
    nt.assert_false(mock_req.called, "calls during init")

    nt.assert_false(connector.token_valid())
    nt.assert_false(mock_req.called, "calls during token validation on None token")
    mock_req.return_value = (
        dict(status='200'), 
        '{"rsp": {"stat":"ok", "frob": "aaaabbbbcccc"}}'
        )

    url, frob = connector.authenticate_desktop()
    nt.assert_equal(frob, "aaaabbbbcccc")
    nt.assert_equal(url, "http://api.rememberthemilk.com/services/auth/?api_key=api-key&format=json&frob=aaaabbbbcccc&perms=write&api_sig=dd165419b28131701a76fb89eab3cef3")

    nt.assert_equal(
        mock_req.call_args_list, 
        [
            (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&format=json&method=rtm.auth.getFrob&api_sig=f56574efbfa4ddc7670c3c4478a48c82',),
             {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
            ]
        #"something called with incorrect arguments"
        )

    mock_req.reset()

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp": {"stat":"ok", "auth": {"token": "33423", "perms": "delete", "user": {"id":"9999", "username" :"Jan", "fullname":"Jan Nowak"}}}}'
        )

    nt.assert_true(
        connector.retrieve_token(frob))
    nt.assert_equal(connector.token, "33423")
    nt.assert_equal(connector.user_name, "Jan")
    nt.assert_equal(connector.user_id, "9999")
    nt.assert_equal(connector.user_full_name, "Jan Nowak")

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&format=json&frob=aaaabbbbcccc&method=rtm.auth.getToken&api_sig=df8ec425a4273dd74c163593ae12ffed',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        #"getToken called with incorrect arguments"
        )

@patch.object(httplib2.Http, 'request')
def test_connectionWithTokenInit(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")
    nt.assert_false(mock_req.called, "calls during init")

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp": {"stat":"ok", "auth": {"token": "33423", "perms": "write", "user": {"id":"9999", "username" :"jan", "fullname":"Jan Nowak"}}}}'
        )

    nt.assert_true(connector.token_valid())
    nt.assert_equal(connector.token, "33423")
    nt.assert_equal(connector.user_name, "jan")
    nt.assert_equal(connector.user_id, "9999")
    nt.assert_equal(connector.user_full_name, "Jan Nowak")

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&format=json&method=rtm.auth.checkToken&api_sig=05aeb55f05449d056d2338b981f94c2f',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        #"getToken called with incorrect arguments"
        )

@patch.object(httplib2.Http, 'request')
def test_tasks_getList(mock_req):
    connector = RtmConnector("api-key", "api-sec", "write", "33423")

    mock_req.return_value = (
        dict(status='200'),
        '{"rsp":{"stat":"ok","tasks":{"rev":"xxx3387c0gkok7jjk0c8coocjaa","list":[{"id":"5384544","taskseries":{"id":"92317232","created":"2010-11-05T11:26:38Z","modified":"2010-11-05T11:26:38Z","name":"Zrobi\u0107 sync \/backup","source":"js","url":"","location_id":"","rrule":{"every":"1","$t":"FREQ=WEEKLY;INTERVAL=2"},"tags":{"tag":["laptop","platon"]},"participants":[],"notes":[],"task":{"id":"137746562","due":"2010-11-04T23:00:00Z","has_due_time":"0","added":"2010-11-05T11:26:38Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}},{"id":"15938247","taskseries":{"id":"91504144","created":"2010-10-29T18:05:24Z","modified":"2010-10-31T16:13:28Z","name":"Wyczy\u015bci\u0107 ~\/@0_ToDo","source":"api","url":"","location_id":"","tags":{"tag":"platon"},"participants":[],"notes":[],"task":{"id":"136365085","due":"2010-11-02T23:00:00Z","has_due_time":"0","added":"2010-10-29T18:05:24Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}},{"id":"15938286","taskseries":{"id":"91929943","created":"2010-11-02T12:47:57Z","modified":"2010-11-02T12:47:57Z","name":"cardapio install","source":"js","url":"","location_id":"","tags":{"tag":"platon"},"participants":[],"notes":[],"task":{"id":"137105711","due":"2010-11-02T23:00:00Z","has_due_time":"0","added":"2010-11-02T12:47:57Z","completed":"","deleted":"","priority":"N","postponed":"0","estimate":""}}}]}}}'
        )
    
    r = connector.call("rtm.tasks.getList", filter="status:incomplete and dueBefore:today and tag:platon")
    #nt.assert_equal(
    assert_structs_equal(
        r,
        {'stat': 'ok', 'tasks': {'list': [{'taskseries': {'task': {'added': '2010-11-05T11:26:38Z', 'deleted': '', 'completed': '', 'due': '2010-11-04T23:00:00Z', 'priority': 'N', 'has_due_time': '0', 'estimate': '', 'postponed': '0', 'id': '137746562'}, 'name': u'Zrobi\u0107 sync /backup', 'created': '2010-11-05T11:26:38Z', 'url': '', 'notes': [], 'tags': {'tag': ['laptop', 'platon']}, 'modified': '2010-11-05T11:26:38Z', 'source': 'js', 'participants': [], 'rrule': {'$t': 'FREQ=WEEKLY;INTERVAL=2', 'every': '1'}, 'location_id': '', 'id': '92317232'}, 'id': '5384544'}, {'taskseries': {'task': {'added': '2010-10-29T18:05:24Z', 'deleted': '', 'completed': '', 'due': '2010-11-02T23:00:00Z', 'priority': 'N', 'has_due_time': '0', 'estimate': '', 'postponed': '0', 'id': '136365085'}, 'name': u'Wyczy\u015bci\u0107 ~/@0_ToDo', 'created': '2010-10-29T18:05:24Z', 'url': '', 'notes': [], 'tags': {'tag': 'platon'}, 'modified': '2010-10-31T16:13:28Z', 'source': 'api', 'participants': [], 'location_id': '', 'id': '91504144'}, 'id': '15938247'}, {'taskseries': {'task': {'added': '2010-11-02T12:47:57Z', 'deleted': '', 'completed': '', 'due': '2010-11-02T23:00:00Z', 'priority': 'N', 'has_due_time': '0', 'estimate': '', 'postponed': '0', 'id': '137105711'}, 'name': 'cardapio install', 'created': '2010-11-02T12:47:57Z', 'url': '', 'notes': [], 'tags': {'tag': 'platon'}, 'modified': '2010-11-02T12:47:57Z', 'source': 'js', 'participants': [], 'location_id': '', 'id': '91929943'}, 'id': '15938286'}], 'rev': 'xxx3387c0gkok7jjk0c8coocjaa'}}
        )

    nt.assert_equal(
        mock_req.call_args, 
        (('http://api.rememberthemilk.com/services/rest/?api_key=api-key&auth_token=33423&filter=status%3Aincomplete+and+dueBefore%3Atoday+and+tag%3Aplaton&format=json&method=rtm.tasks.getList&api_sig=1987fb50732b7f749475358ee8cef43c',),
         {'headers': {'Cache-Control': 'no-cache, max-age=0'}})
        #"getToken called with incorrect arguments"
        )

