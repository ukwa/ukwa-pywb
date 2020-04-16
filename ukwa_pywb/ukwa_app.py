from werkzeug.contrib.sessions import SessionMiddleware, SessionStore, Session
from werkzeug.routing import Map, Rule
from werkzeug.http import parse_authorization_header

import time
import os
import re

from redis import StrictRedis

import urllib.parse

from pywb.rewrite.wburl import WbUrl

from pywb.apps.frontendapp import FrontEndApp
from pywb.apps.rewriterapp import RewriterApp, UpstreamException
from pywb.rewrite.templateview import BaseInsertView

from pywb.apps.cli import ReplayCli

from pywb.apps.wbrequestresponse import WbResponse


# ============================================================================
COOKIE_NAME = '_ukwa_pywb_sesh'
SESSION_KEY = 'ukwa.pywb.session'

SESH_LIST = 'sesh:{0}'

LOCK_PING_EXPIRE = None

DEFAULT_TTL = 86400

SESSION_TTL = DEFAULT_TTL

LOCK_KEY = 'lock:{coll}/{ts}/{url}'


# ============================================================================
def authorize(func):
    def check_auth(self, environ, *args, **kwargs):
        LOCKS_AUTH = os.environ.get('LOCKS_AUTH', '')

        if ':' in LOCKS_AUTH:
            allowed = False
            auth = parse_authorization_header(environ.get('HTTP_AUTHORIZATION'))
            username, password = LOCKS_AUTH.split(':', 1)
            if auth and auth.username == username  and auth.password == password:
                allowed = True
        else:
            allowed = True

        if allowed:
            return func(self, environ, *args, **kwargs)
        else:
            raise UpstreamException(401, '', 'not-authorized')

    return check_auth


# ============================================================================
class RedisSessionStore(SessionStore):
    def __init__(self, redis):
        super(RedisSessionStore, self).__init__(session_class=LockingSession)
        self.redis = redis

    def new(self):
        id_ = self.generate_key()
        return LockingSession(self.redis, {}, id_, new=True)

    def get(self, sid):
        return LockingSession(self.redis, {}, sid, new=False)


# ============================================================================
class LockingSession(Session):
    def __init__(self, redis, *args, **kwargs):
        super(LockingSession, self).__init__(*args, **kwargs)

        self.redis = redis

    def is_locked(self, lock_key):
        res = self.redis.get(lock_key)
        if not res:
            return False

        value = self.redis.get(lock_key)
        return value != self.sid

    def lock(self, lock_key):
        if not self.redis.setnx(lock_key, self.sid):
            value = self.redis.get(lock_key)
            if value != self.sid:
                return False

        sesh_list = SESH_LIST.format(self.sid)

        # new session, save cookie
        if not self.redis.exists(sesh_list):
            self.modified = True

        self.redis.sadd(sesh_list, lock_key)

        # set both keys to expire at end of the day
        next_day = int(time.time())

        # clamp to exact boundary if set to default (eg. day)
        # otherwise, expire in TTL seconds
        if SESSION_TTL == DEFAULT_TTL:
            next_day += SESSION_TTL - (next_day % SESSION_TTL)
        else:
            next_day += SESSION_TTL

        self.redis.expireat(sesh_list, next_day)
        self.redis.expireat(lock_key, next_day)
        return True


# ============================================================================
class UKWARewriter(RewriterApp):
    WB_URL_RX = re.compile(r'[\d]{1,14}/.*')

    def get_lock_url(self, wb_url, full_prefix, environ):
        # don't lock embeds
        if wb_url.mod != 'mp_':
            return None

        # don't lock ajax
        if self.is_ajax(environ):
            return None

        referrer = environ.get('HTTP_REFERER')
        # if no referrer, probably should lock
        if not referrer:
            return wb_url

        # if referrer is a .css, still an embed
        if referrer.endswith('.css'):
            return None

        if referrer.startswith(full_prefix):
            referrer = referrer[len(full_prefix):]
            m = self.WB_URL_RX.search(referrer)
            if m:
                return WbUrl(m.group(0))

        return None

    def handle_custom_response(self, environ, wb_url, full_prefix, host_prefix, kwargs):
        if kwargs.get('single-use-lock'):
            environ['single_use_lock'] = True
            environ['select_word_limit'] = SELECT_WORD_LIMIT
            environ['lock_ping_interval'] = LOCK_PING_INTERVAL * 1000

            lock_wb_url = self.get_lock_url(wb_url, full_prefix, environ)
            if lock_wb_url:
                session = environ[SESSION_KEY]
                curr_key = LOCK_KEY.format(coll=kwargs.get('coll', ''),
                                           ts=wb_url.timestamp,
                                           url=wb_url.url)

                if session.is_locked(curr_key):
                    raise UpstreamException(403, str(wb_url), 'access-locked')

                lock_key = LOCK_KEY.format(coll=kwargs.get('coll', ''),
                                           ts=lock_wb_url.timestamp,
                                           url=lock_wb_url.url)

                session.lock(lock_key)

        return super(UKWARewriter, self).handle_custom_response(environ, wb_url, full_prefix, host_prefix, kwargs)

    def _error_response(self, environ, wbe):
        response = super(UKWARewriter, self)._error_response(environ, wbe)
        if wbe.status_code == 401:
            response.status_headers.headers.append(('WWW-Authenticate', 'Basic realm=Auth Required'))

        return response

    def render_content(self, wb_url_str, coll_config, environ):
        default_response = super(UKWARewriter, self).render_content(wb_url_str, coll_config, environ)

        add_headers = coll_config.get('add_headers') or {}
        for header in add_headers:
            default_response.status_headers[header] = add_headers[header]

        ct_redirects = coll_config.get('content_type_redirects')
        if not ct_redirects:
            return default_response

        # not an actual response
        if not default_response.status_headers.get('memento-datetime'):
            return default_response

        # don't redirect raw responses, needed for viewer access
        if default_response.status_headers.get('preference-applied') == 'raw':
            return default_response

        content_type = default_response.status_headers.get("content-type")

        redirect_url = None

        if content_type:
            content_type = content_type.split(";", 1)[0]
            redirect_url = ct_redirects.get(content_type)
            if redirect_url is None:
                redirect_url = ct_redirects.get(content_type.split("/")[0] + "/")

        # if no content-type match, check content-disposition
        if not redirect_url:
            content_disp = default_response.status_headers.get("content-disposition")
            if content_disp and 'attachment' in content_disp:
                redirect_url = ct_redirects.get('<any-download>')

        if not redirect_url:
            return default_response

        wb_url = WbUrl(wb_url_str)
        wb_url.mod = 'id_'
        loc = self.get_full_prefix(environ) + str(wb_url)

        query = urllib.parse.urlencode({'url': loc})
        final_url = redirect_url.format(query=query)
        return WbResponse.redir_response(final_url)


# ============================================================================
class UKWApp(FrontEndApp):
    REWRITER_APP_CLS = UKWARewriter

    REFER_WB_URL_RX = re.compile(r'(\w+)/([\d]{1,14}(?:\w\w_)?/.*)')

    def _init_routes(self):
        super(UKWApp, self)._init_routes()
        self.url_map.add(Rule('/_locks/clear_url/<path:url>', endpoint=self.lock_clear_url))
        self.url_map.add(Rule('/_locks/clear/<id>', endpoint=self.lock_clear_session))
        self.url_map.add(Rule('/_locks/reset', endpoint=self.lock_clear_all))
        self.url_map.add(Rule('/_locks/ping', endpoint=self.lock_ping_reset))
        self.url_map.add(Rule('/_locks', endpoint=self.lock_listing))

        self.url_map.add(Rule('/_logout', endpoint=self.log_out))

    def lock_ping_reset(self, environ):
        referrer = environ.get('HTTP_REFERER')
        if not referrer:
            return WbResponse.json_response({})

        full_prefix = self.rewriterapp.get_full_prefix(environ)

        if not referrer.startswith(full_prefix):
            return WbResponse.json_response({})

        referrer = referrer[len(full_prefix):]
        m = self.REFER_WB_URL_RX.match(referrer)
        if not m:
            return WbResponse.json_response({})

        wb_url = WbUrl(m.group(2))

        lock_key = LOCK_KEY.format(coll=m.group(1),
                                   ts=wb_url.timestamp,
                                   url=wb_url.url)

        session = environ[SESSION_KEY]
        if self.lock_ping_extend_time and not session.is_locked(lock_key):
            res = session.redis.expire(lock_key, self.lock_ping_extend_time)

        return WbResponse.json_response({})

    @authorize
    def lock_clear_url(self, environ, url):
        if environ.get('QUERY_STRING'):
            url += '?' + environ.get('QUERY_STRING')

        redis = environ[SESSION_KEY].redis

        lock_key = 'lock:' + url

        sesh = redis.get(lock_key)
        redis.delete(lock_key)

        # check if has session (may be not existant lock) and remove from it
        if sesh:
            redis.srem(SESH_LIST.format(sesh), lock_key)

        return WbResponse.redir_response('/_locks')

    @authorize
    def lock_clear_all(self, environ):
        redis = environ[SESSION_KEY].redis

        for sesh_key in redis.scan_iter(SESH_LIST.format('*')):
            redis.delete(sesh_key)

        for lock_key in redis.scan_iter('lock:*'):
            redis.delete(lock_key)

        return WbResponse.redir_response('/_locks')

    @authorize
    def lock_clear_session(self, environ, id):
        self._clear_session(environ, id)

        return WbResponse.redir_response('/_locks')

    def log_out(self, environ):
        self._clear_session(environ)

        return WbResponse.redir_response('/')

    def _clear_session(self, environ, id_=None):
        redis = environ[SESSION_KEY].redis
        if not id_:
            id_ = environ[SESSION_KEY].sid

        sesh_key = SESH_LIST.format(id_)
        locks = redis.smembers(sesh_key)
        for lock in locks:
            redis.delete(lock)

        redis.delete(sesh_key)

    @authorize
    def lock_listing(self, environ):
        lock_view = BaseInsertView(self.rewriterapp.jinja_env, 'locks.html')

        session = environ[SESSION_KEY]

        sessions = {}

        for sesh_key in session.redis.scan_iter(SESH_LIST.format('*')):
            sesh = sesh_key.split(':')[1]

            sessions[sesh] = [key[5:] for key in session.redis.smembers(sesh_key)]

        content = lock_view.render_to_string(environ,
                                             current=session.sid,
                                             sessions=sessions)

        return WbResponse.text_response(content, content_type='text/html; charset="utf-8"')

    @classmethod
    def init_app(cls, config_file=None, extra_config=None):
        global SESSION_TTL

        try:
            SESSION_TTL = int(os.environ.get('TEST_SESSION_LOCK_INTERVAL'))
        except:  #pragma: no cover
            SESSION_TTL = DEFAULT_TTL

        # ping extend time
        cls.lock_ping_extend_time = int(os.environ.get('LOCK_PING_EXTEND_TIME', 0))

        # ping every interval seconds
        global LOCK_PING_INTERVAL
        LOCK_PING_INTERVAL = int(os.environ.get('LOCK_PING_INTERVAL', 10))

        # select word limit
        global SELECT_WORD_LIMIT
        SELECT_WORD_LIMIT = int(os.environ.get('SELECT_WORD_LIMIT', 0))


        REDIS_URL = os.environ.get('REDIS_URL')
        if REDIS_URL:
            r = StrictRedis.from_url(REDIS_URL, decode_responses=True)
        else:
            print('WARNING: No REDIS_URL defined.. Using Fake Redis.. Session Locks will not persist on restart')
            from fakeredis import FakeStrictRedis
            r = FakeStrictRedis(decode_responses=True)

        app = UKWApp(config_file=config_file, custom_config=extra_config)
        app = SessionMiddleware(app, RedisSessionStore(r),
                                cookie_name=COOKIE_NAME,
                                environ_key=SESSION_KEY,
                                cookie_httponly=True,
                                cookie_age=SESSION_TTL)
        return app


#=============================================================================
class UKWACli(ReplayCli):
    def load(self):
        super(UKWACli, self).load()

        # Optional debug mode:
        DEBUG = os.environ.get('DEBUG', False)
        if DEBUG:
            self.extra_config['debug'] = True

        return UKWApp.init_app()


#=============================================================================
def ukwa(args=None):  #pragma: no cover
    return UKWACli(args=args,
                   default_port=8080,
                   desc='UKWA Wayback Machine Server')


# ============================================================================
def main(args=None):  #pragma: no cover
    ukwa().run()


# ============================================================================
if __name__ == "__main__":  #pragma: no cover
    main()
