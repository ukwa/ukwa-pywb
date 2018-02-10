from werkzeug.contrib.sessions import SessionMiddleware, SessionStore, Session

import time
import os

from redis import StrictRedis

from pywb.apps.frontendapp import FrontEndApp
from pywb.apps.rewriterapp import RewriterApp, UpstreamException

from pywb.apps.cli import ReplayCli

from pywb.apps.wbrequestresponse import WbResponse


# ============================================================================
COOKIE_NAME = '_ukwa_pywb_sesh'
SESSION_KEY = 'ukwa.pywb.session'

SESH_LIST = 'sesh:{0}'
ALL_SESH = 'all_sessions'

SESSION_TTL = 86400
LOCK_KEY = 'lock:{coll}/{ts}/{url}'


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
        next_day += SESSION_TTL - (next_day % SESSION_TTL)

        self.redis.expireat(sesh_list, next_day)
        self.redis.expireat(lock_key, next_day)
        return True


# ============================================================================
class RateLimitRewriterApp(RewriterApp):
    def __init__(self, *args, **kwargs):
        super(RateLimitRewriterApp, self).__init__(*args, **kwargs)

    def should_lock(self, wb_url, environ):
        if wb_url.mod == 'mp_' and not self.is_ajax(environ):
            return True

        return False

    def handle_custom_response(self, environ, wb_url, full_prefix, host_prefix, kwargs):
        if self.should_lock(wb_url, environ):
            session = environ[SESSION_KEY]
            lock_key = LOCK_KEY.format(coll=kwargs.get('coll', ''),
                                       ts=wb_url.timestamp,
                                       url=wb_url.url)

            if not session.lock(lock_key):
                #raise UpstreamException(403, str(wb_url), 'Sorry, access this url is currently locked')
                return WbResponse.text_response('Not Allowed', status='403 Locked')

        return super(RateLimitRewriterApp, self).handle_custom_response(environ, wb_url, full_prefix, host_prefix, kwargs)


# ============================================================================
class UKWApp(FrontEndApp):
    REWRITER_APP_CLS = RateLimitRewriterApp


#=============================================================================
class WaybackCli(ReplayCli):
    def load(self, config_file=None):
        super(WaybackCli, self).load()

        REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

        r = StrictRedis.from_url(REDIS_URL, decode_responses=True)

        app = UKWApp(config_file=config_file, custom_config=self.extra_config)
        app = SessionMiddleware(app, RedisSessionStore(r),
                                cookie_name=COOKIE_NAME,
                                environ_key=SESSION_KEY,
                                cookie_httponly=True,
                                cookie_age=SESSION_TTL * 2)
        return app


#=============================================================================
def wayback(args=None):  #pragma: no cover
    return WaybackCli(args=args,
                      default_port=8080,
                      desc='pywb Wayback Machine Server').run()


# ============================================================================
if __name__ == "__main__":  #pragma: no cover
    wayback()

