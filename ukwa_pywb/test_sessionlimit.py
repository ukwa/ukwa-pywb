#from gevent import monkey; monkey.patch_all(thread=False)

import pytest
import webtest
import os
import time

from pywb.warcserver.test.testutils import BaseTestClass

from fakeredis import FakeStrictRedis


# ============================================================================
class TestSessionLimitApp(BaseTestClass):
    sesh_one = None

    @classmethod
    def get_test_app(cls, config_file, custom_config=None):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)

        os.environ['SESSION_LOCK_INTERVAL'] = '3'
        import ukwa_pywb.ratelimitapp
        ukwa_pywb.ratelimitapp.StrictRedis = FakeStrictRedis
        app = ukwa_pywb.ratelimitapp.WaybackCli(args=['--debug']).load(config_file=config_file)
        return app, webtest.TestApp(app)

    @classmethod
    def get_session(cls):
        return cls.testapp.cookies['_ukwa_pywb_sesh'].strip('"')

    @classmethod
    def setup_class(cls):
        super(TestSessionLimitApp, cls).setup_class()
        cls.app, cls.testapp = cls.get_test_app('./test_config.yaml')
        cls.redis = FakeStrictRedis(decode_responses=True)

    def test_replay_top_frame_no_lock(self):
        res = self.testapp.get('/pywb/acid.matkelly.com/', status=200)

        # set not used yet, don't set cookie
        assert 'Set-Cookie' not in res.headers

        assert self.redis.keys('*') == []

    def test_replay_1_lock(self):
        res = self.testapp.get('/pywb/mp_/acid.matkelly.com/', status=307)

        # set cookie first time session use
        assert 'Set-Cookie' in res.headers

        # lock exists!
        assert self.redis.exists('lock:pywb//http://acid.matkelly.com/')

        res = res.follow()
        assert 'Set-Cookie' not in res.headers

        sesh_keys = self.redis.keys('sesh:*')
        assert len(sesh_keys) == 1

        assert self.redis.smembers(sesh_keys[0]) == {'lock:pywb//http://acid.matkelly.com/', 'lock:pywb/20180203004147/http://acid.matkelly.com/'}

        sesh = sesh_keys[0].split(':')[1]
        assert self.get_session() == sesh

        assert self.redis.get('lock:pywb//http://acid.matkelly.com/') == sesh
        assert self.redis.get('lock:pywb/20180203004147/http://acid.matkelly.com/') == sesh


    def test_replay_no_lock_embed(self):
        res = self.testapp.get('/pywb/im_/acid.matkelly.com/pixel.png')
        assert not self.redis.exists('lock:pywb//http://acid.matkelly.com/pixel.png')

    def test_replay_again_same_session(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/')

        assert len(self.redis.keys('lock:*')) == 2

    def test_replay_blocked(self):
        TestSessionLimitApp.sesh_one = self.redis.keys('sesh:*')[0].split(':')[1]
        self.testapp.cookiejar.clear()

        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=403)

        # not setting cookie until used
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

    def test_replay_expired(self):
        time.sleep(3)

        assert not self.redis.exists('lock:pywb//http://acid.matkelly.com/')
        assert not self.redis.exists('lock:pywb/20180203004147/http://acid.matkelly.com/')

        assert self.redis.keys('*') == []

        res = self.testapp.get('/pywb/20140716200243mp_/acid.matkelly.com/', status=200)

        # cookie hasn't expired yet, so refresh the expiry for another interval
        assert '=' + self.sesh_one in res.headers['Set-Cookie']
        assert 'Max-Age=3' in res.headers['Set-Cookie']

    def test_replay_cookie_already_set(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/?_=123', status=307)
        assert 'Set-Cookie' not in res.headers

        #NOTE: fuzzy redirect to first capture, not closest!
        assert res.location.endswith('/pywb/20140716200243mp_/http://acid.matkelly.com/')

    def test_locks_view(self):
        res = self.testapp.get('/_locks')

        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123' in res.text
        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/' in res.text
        assert '/_locks/clear_url/pywb/20140716200243/http://acid.matkelly.com/' in res.text

    def test_locks_clear_url(self):
        # clear url
        res = self.testapp.get('/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123', status=302)
        res = res.follow()

        # cleared
        assert '/_locks/clear_url/pywb/20180203004147/http://acid.matkelly.com/?_=123' not in res.text

        # non-existant lock clear, just ignore
        new_res = self.testapp.get('/_locks/clear_url/pywb/20180203004147/foobar', status=302)
        assert new_res.location.endswith('/_locks')

        # not cleared yet
        assert '/_locks/clear_url/pywb/20140716200243/http://acid.matkelly.com/' in res.text
        assert '"/_locks/clear/{0}"'.format(self.get_session()) in res.text

    def test_clear_sesh(self):
        # clear session
        res = self.testapp.get('/_locks/clear/{0}'.format(self.get_session()), status=302)
        res = res.follow()

        assert '"/_locks/clear/{0}"'.format(self.get_session()) not in res.text

        assert self.redis.keys('*') == []

    def test_logout(self):
        res = self.testapp.get('/pywb/20180203004147mp_/acid.matkelly.com/', status=200)

        assert self.redis.smembers('sesh:' + self.get_session()) == {'lock:pywb/20180203004147/http://acid.matkelly.com/'}

        res = self.testapp.get('/_locks/clear', status=302)
        assert res.location.endswith('/_locks')

        assert self.redis.smembers('sesh:' + self.get_session()) == set()


