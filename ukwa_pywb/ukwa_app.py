from werkzeug.contrib.sessions import SessionMiddleware, SessionStore, Session
from werkzeug.routing import Map, Rule
from werkzeug.http import parse_authorization_header

import time
import os
from urllib.parse import quote

from redis import StrictRedis

from babel.support import Translations
from jinja2 import contextfunction
from werkzeug.routing import Submount

from pywb.rewrite.templateview import JinjaEnv

from pywb.apps.frontendapp import FrontEndApp
from pywb.apps.rewriterapp import RewriterApp, UpstreamException
from pywb.rewrite.templateview import BaseInsertView

from pywb.apps.cli import ReplayCli

from pywb.apps.wbrequestresponse import WbResponse


# ============================================================================
COOKIE_NAME = '_ukwa_pywb_sesh'
SESSION_KEY = 'ukwa.pywb.session'

SESH_LIST = 'sesh:{0}'

DEFAULT_TTL = 86400

SESSION_TTL = DEFAULT_TTL

LOCK_KEY = 'lock:{coll}/{ts}/{url}'


# ============================================================================
def authorize(func):
    def check_auth(self, environ, *args, **kwargs):
        LOCKS_USERNAME = os.environ.get('LOCKS_USERNAME', '')
        LOCKS_PASSWORD = os.environ.get('LOCKS_PASSWORD', '')

        if LOCKS_USERNAME and LOCKS_PASSWORD:
            allowed = False
            auth = parse_authorization_header(environ.get('HTTP_AUTHORIZATION'))
            if auth and auth.username == LOCKS_USERNAME  and auth.password == LOCKS_PASSWORD:
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
    def __init__(self, *args, **kwargs):
        jinja_env = JinjaEnv(globals={'static_path': 'static'},
                             extensions=['jinja2.ext.i18n', 'jinja2.ext.with_'])

        kwargs['jinja_env'] = jinja_env
        super(UKWARewriter, self).__init__(*args, **kwargs)

        self.init_loc(jinja_env)

    def init_loc(self, jinja_env):
        self.loc_map = {}

        locales_root_dir = self.config.get('locales_root_dir')
        locales = self.config.get('locales')
        locales = locales or []

        for loc in locales:
            self.loc_map[loc] = Translations.load(locales_root_dir, [loc, 'en'])
            #jinja_env.jinja_env.install_gettext_translations(translations)

        def get_translate(context):
            loc = context.get('env', {}).get('pywb_lang')
            return self.loc_map.get(loc)

        def override_func(jinja_env, name):
            @contextfunction
            def get_override(context, text):
                translate = get_translate(context)
                if not translate:
                    return text

                func = getattr(translate, name)
                return func(text)

            jinja_env.globals[name] = get_override

        override_func(jinja_env.jinja_env, 'gettext')
        override_func(jinja_env.jinja_env, 'ngettext')

        @contextfunction
        def quote_gettext(context, text):
            translate = get_translate(context)
            if not translate:
                return text

            text = translate.gettext(text)
            return quote(text, safe='/: ')

        jinja_env.jinja_env.globals['locales'] = list(self.loc_map.keys())
        jinja_env.jinja_env.globals['_Q'] = quote_gettext

        @contextfunction
        def switch_locale(context, locale):
            environ = context.get('env')
            request_uri = environ.get('REQUEST_URI', environ.get('PATH_INFO'))
            curr_loc = environ.get('pywb_lang', '')
            if curr_loc:
                return request_uri.replace(curr_loc, locale, 1)
            else:
                return '/' + locale + request_uri

        jinja_env.jinja_env.globals['switch_locale'] = switch_locale

    def should_lock(self, wb_url, environ):
        if wb_url.mod == 'mp_' and not self.is_ajax(environ):
            return True

        return False

    def handle_custom_response(self, environ, wb_url, full_prefix, host_prefix, kwargs):
        if kwargs.get('single-use-lock') and self.should_lock(wb_url, environ):
            session = environ[SESSION_KEY]
            lock_key = LOCK_KEY.format(coll=kwargs.get('coll', ''),
                                       ts=wb_url.timestamp,
                                       url=wb_url.url)

            if not session.lock(lock_key):
                raise UpstreamException(403, str(wb_url), 'access-locked')

        return super(UKWARewriter, self).handle_custom_response(environ, wb_url, full_prefix, host_prefix, kwargs)


# ============================================================================
class UKWApp(FrontEndApp):
    REWRITER_APP_CLS = UKWARewriter

    def _init_routes(self):
        super(UKWApp, self)._init_routes()
        self.url_map.add(Rule('/_locks/clear_url/<path:url>', endpoint=self.lock_clear_url))
        self.url_map.add(Rule('/_locks/clear/<id>', endpoint=self.lock_clear_session))
        self.url_map.add(Rule('/_locks/reset', endpoint=self.lock_clear_all))
        self.url_map.add(Rule('/_locks', endpoint=self.lock_listing))

        self.url_map.add(Rule('/_logout', endpoint=self.log_out))

    def _init_coll_routes(self, coll_prefix):
        routes = self._make_coll_routes(coll_prefix)

        # init loc routes, if any
        loc_keys = list(self.rewriterapp.loc_map.keys())
        if loc_keys:
            routes.append(Rule('/', endpoint=self.serve_home))

            submount_route = ', '.join(loc_keys)
            submount_route = '/<any({0}):lang>'.format(submount_route)

            self.url_map.add(Submount(submount_route, routes))

        for route in routes:
            self.url_map.add(route)

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
        REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

        global SESSION_TTL

        try:
            SESSION_TTL = int(os.environ.get('SESSION_LOCK_INTERVAL'))
        except:  #pragma: no cover
            SESSION_TTL = DEFAULT_TTL

        r = StrictRedis.from_url(REDIS_URL, decode_responses=True)

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

        return UKWApp.init_app()


#=============================================================================
def ukwa(args=None):  #pragma: no cover
    return UKWACli(args=args,
                   default_port=8080,
                   desc='UKWA Wayback Machinee Server')


# ============================================================================
def main(args=None):  #pragma: no cover
    ukwa().run()


# ============================================================================
if __name__ == "__main__":  #pragma: no cover
    main()
