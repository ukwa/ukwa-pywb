#from gevent import monkey; monkey.patch_all(thread=False)

import pytest
import webtest
import os
import time
import base64

from fakeredis import FakeStrictRedis

from ukwa_pywb.test.testbase import TestClass

# ============================================================================
class TestSingleUseLock(TestClass):
    sesh_one = None

    @classmethod
    def get_session(cls):
        return cls.testapp.cookies['_ukwa_pywb_sesh'].strip('"')

    def get_auth_headers(self):
        return {'Authorization': 'basic ' + base64.b64encode(b'ukwa-admin:testpass').decode('utf-8')}

    @classmethod
    def setup_class(cls):
        super(TestSingleUseLock, cls).setup_class()

        os.environ['TEST_SESSION_LOCK_INTERVAL'] = '5'
        os.environ['LOCK_PING_EXTEND_TIME'] = '2'
        os.environ['LOCK_PING_INTERVAL'] = '10'
        os.environ['LOCKS_AUTH'] = 'ukwa-admin:testpass'
        os.environ['SELECT_WORD_LIMIT'] = '20'

        cls.testapp = cls.get_test_app()

        cls.redis = FakeStrictRedis(decode_responses=True)

    @classmethod
    def teardown_class(cls):
        del os.environ['LOCKS_AUTH']
        del os.environ['TEST_SESSION_LOCK_INTERVAL']
        super(TestSingleUseLock, cls).teardown_class()

    def test_replay_top_frame_no_lock(self):
        res = self.testapp.get('/pywb/acid.matkelly.com/', status=307)

        # set not used yet, don't set cookie
        assert 'Set-Cookie' not in res.headers

        assert self.redis.keys('*') == []

        res = res.follow()

        # ensure ping is added
        assert 'setInterval(function () { window.fetch("/_locks/ping"); }, 10000);' in res.text

    def test_replay_1_lock(self):
        res = self.testapp.get('/pywb/mp_/acid.matkelly.com/', status=307)

        # set cookie first time session use
        assert 'Set-Cookie' in res.headers

        # lock exists!
        assert self.redis.exists('lock:pywb//http://acid.matkelly.com/')

        res = res.follow()
        assert 'Set-Cookie' not in res.headers

        # ensure selection limit is added
        print(res.text)
        assert '__WB_initSelectionLimit(20);' in res.text

        sesh_keys = self.redis.keys('sesh:*')
        assert len(sesh_keys) == 1

        assert self.redis.smembers(sesh_keys[0]) == {'lock:pywb//http://acid.matkelly.com/', 'lock:pywb/20180203004147/http://acid.matkelly.com/'}

        sesh = sesh_keys[0].split(':')[1]
        assert self.get_session() == sesh

        assert self.redis.get('lock:pywb//http://acid.matkelly.com/') == sesh
        assert self.redis.get('lock:pywb/20180203004147/http://acid.matkelly.com/') == sesh


    def test_replay_no_lock_embed(self):
        res = self.testapp.get('/pywb/im_/acid.matkelly.com/pixel.png')
        assert res.headers['Cache-Control'] == 'max-age=0, no-cache, must-revalidate, proxy-revalidate, private'
        assert not self.redis.exists('lock:pywb//http://acid.matkelly.com/pixel.png')

    def test_replay_again_same_session(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/')

        assert len(self.redis.keys('lock:*')) == 2

    def test_replay_content_type_redirect_viewer(self):
        res = self.testapp.get('/pywb/20200415232829mp_/https://example.com/TestDocument.rtf', status=302)
        assert res.location == 'https://example.com/viewer?url=http%3A%2F%2Flocalhost%3A80%2Fpywb%2F20200415232829id_%2Fhttps%3A%2F%2Fexample.com%2FTestDocument.rtf'

        res = self.testapp.get('/pywb/20200415232829id_/https://example.com/TestDocument.rtf', status=200)
        assert res.headers['Cache-Control'] == 'max-age=0, no-cache, must-revalidate, proxy-revalidate, private'

    def test_replay_content_type_redirect_blocked(self):
        res = self.testapp.get('/pywb/20200415232823mp_/https://example.com/TestDocument.docx', status=302)
        assert res.location == 'https://example.com/blocked?url=http%3A%2F%2Flocalhost%3A80%2Fpywb%2F20200415232823id_%2Fhttps%3A%2F%2Fexample.com%2FTestDocument.docx'

        res = self.testapp.get('/pywb/20200415232823id_/https://example.com/TestDocument.docx', status=200)
        assert res.headers['Cache-Control'] == 'max-age=0, no-cache, must-revalidate, proxy-revalidate, private'

    def test_replay_content_disposition_redirect_blocked(self):
        res = self.testapp.get('/pywb/20200416010916mp_/https://example.com/download/afile', status=302)
        assert res.location == 'https://example.com/blocked?url=http%3A%2F%2Flocalhost%3A80%2Fpywb%2F20200416010916id_%2Fhttps%3A%2F%2Fexample.com%2Fdownload%2Fafile'

        res = self.testapp.get('/pywb/20200416010916id_/https://example.com/download/afile', status=200)
        assert res.headers['Content-Type'] == 'text/plain'
        assert res.headers['Cache-Control'] == 'max-age=0, no-cache, must-revalidate, proxy-revalidate, private'
        assert res.headers['Content-Disposition'] == 'attachment; filename="somefile.txt"'


    def test_replay_blocked(self):
        TestSingleUseLock.sesh_one = self.redis.keys('sesh:*')[0].split(':')[1]
        self.testapp.cookiejar.clear()

        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=403)
        res = self.testapp.get('/pywb/20200415232823mp_/https://example.com/TestDocument.docx', status=403)
        res = self.testapp.get('/pywb/20200415232829mp_/https://example.com/TestDocument.rtf', status=403)
        res = self.testapp.get('/pywb/20200416010916mp_/https://example.com/download/afile', status=403)

        # not setting cookie until used
        assert 'Set-Cookie' not in res.headers

    def test_replay_diff_coll_no_locks(self):
        self.testapp.cookiejar.clear()

        res = self.testapp.get('/pywb-no-locks/20180203004147mp_/acid.matkelly.com/', status=200)

        # not locking,
        assert 'Set-Cookie' not in res.headers

    def test_replay_no_lock_different_ts(self):
        res = self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/')
        assert self.redis.exists('lock:pywb/20140716200243/http://acid.matkelly.com/')

        assert self.get_session() != self.sesh_one

    def test_two_sessions(self):
        assert len(self.redis.keys('sesh:*')) == 2

        # second session
        self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/', status=200)
        self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=403)

        self.testapp.cookiejar.clear()
        self.testapp.set_cookie('_ukwa_pywb_sesh', self.sesh_one)

        assert self.get_session() == self.sesh_one

        # back to first
        self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/', status=403)
        self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=200)

    def test_ping_lock(self):
        self.testapp.get('/_locks/ping',
            headers={'Referer': 'http://localhost:80/pywb/20180203004147mp_/acid.matkelly.com/'}, status=200)

        res = self.redis.ttl('lock:pywb/20180203004147/http://acid.matkelly.com/')
        assert res > 0 and res <= 2
        assert self.redis.ttl('lock:pywb/20140716200243/http://acid.matkelly.com/') > 2

    def test_replay_expired(self):
        time.sleep(5)

        assert not self.redis.exists('lock:pywb//http://acid.matkelly.com/')
        assert not self.redis.exists('lock:pywb/20180203004147/http://acid.matkelly.com/')

        assert self.redis.keys('*') == []

        res = self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/', status=200)

        # cookie hasn't expired yet, so refresh the expiry for another interval
        assert '=' + self.sesh_one in res.headers['Set-Cookie']
        assert 'Max-Age=5' in res.headers['Set-Cookie']

    def test_replay_cookie_already_set(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/?_=123', status=307)
        assert 'Set-Cookie' not in res.headers

        #NOTE: fuzzy redirect to first capture, not closest!
        assert res.location.endswith('/pywb/20140716200243mp_/http://acid.matkelly.com/')

    def test_locks_auth_needed(self):
        res = self.testapp.get('/_locks', status=401)
        res = self.testapp.get('/_locks/clear_url/pywb/20180203004147/foobar', status=401)
        res = self.testapp.get('/_locks/reset', status=401)
        res = self.testapp.get('/_locks/clear/{0}'.format(self.get_session()), status=401)

        assert res.headers['WWW-Authenticate'] == 'Basic realm=Auth Required'

    def test_locks_view(self):
        res = self.testapp.get('/_locks', headers=self.get_auth_headers())

        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123' in res.text
        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/' in res.text
        assert '/_locks/clear_url/pywb/20140716200243/http://acid.matkelly.com/' in res.text

        assert '/_locks/clear/' in res.text
        assert '/_locks/reset' in res.text
        assert '/_logout' in res.text

    def test_locks_clear_url(self):
        # clear url
        res = self.testapp.get('/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123', status=302, headers=self.get_auth_headers())
        res = res.follow(headers=self.get_auth_headers())

        # cleared
        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123' not in res.text

        # non-existant lock clear, just ignore
        new_res = self.testapp.get('/_locks/clear_url/pywb/20180203004147/foobar', status=302, headers=self.get_auth_headers())
        assert new_res.location.endswith('/_locks')

        # not cleared yet
        assert '/_locks/clear_url/pywb/20140716200243/http://acid.matkelly.com/' in res.text
        assert '"/_locks/clear/{0}"'.format(self.get_session()) in res.text

    def test_clear_sesh(self):
        # clear session
        res = self.testapp.get('/_locks/clear/{0}'.format(self.get_session()), status=302, headers=self.get_auth_headers())
        res = res.follow(headers=self.get_auth_headers())

        assert '"/_locks/clear/{0}"'.format(self.get_session()) not in res.text

        assert self.redis.keys('*') == []

    def test_logout(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=200)

        assert self.redis.smembers('sesh:' + self.get_session()) == {'lock:pywb/20180203004147/http://acid.matkelly.com/'}

        res = self.testapp.get('/_logout', status=302)
        assert res.location.endswith('/')

        assert self.redis.smembers('sesh:' + self.get_session()) == set()

        assert self.redis.keys('*') == []

    def test_clear_all(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=200)
        self.testapp.cookiejar.clear()
        res = self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/', status=200)
        self.testapp.cookiejar.clear()
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/?_=123', status=307)

        assert len(self.redis.keys('sesh:*')) == 3
        assert len(self.redis.keys('lock:*')) == 3

        res = self.testapp.get('/_locks/reset', status=302, headers=self.get_auth_headers())
        res = res.follow(headers=self.get_auth_headers())

        assert 'No Session Locks' in res.text
        assert self.redis.keys('*') == []

    def test_no_auth(self):
        os.environ['LOCKS_AUTH'] = ''

        res = self.testapp.get('/_locks', status=200)

