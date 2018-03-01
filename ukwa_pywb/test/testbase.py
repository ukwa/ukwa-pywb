import os
import webtest

from pywb.warcserver.test.testutils import BaseTestClass, FakeRedisTests
from fakeredis import FakeStrictRedis

# ============================================================================
class TestClass(FakeRedisTests, BaseTestClass):
    @classmethod
    def get_test_app(cls, config_file='./config_test.yaml', custom_config=None):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)

        import ukwa_pywb.ukwa_app
        app = ukwa_pywb.ukwa_app.UKWApp.init_app(config_file=config_file,
                                                 extra_config=dict(debug=True))
        return webtest.TestApp(app)


