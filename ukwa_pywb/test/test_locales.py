from ukwa_pywb.test.testbase import TestClass

# ============================================================================
class TestLocale(TestClass):
    @classmethod
    def setup_class(cls):
        super(TestLocale, cls).setup_class()

        cls.testapp = cls.get_test_app()

    def test_locale_en_home(self):
        res = self.testapp.get('/en/')

        assert 'UK Web Archive Access System' in res.text

    def test_locale_cy_home(self):
        res = self.testapp.get('/cy/')

        assert "System fynediad Archif We y DG" in res.text

    def test_locale_en_replay_banner(self):
        res = self.testapp.get('/en/pywb-no-locks/mp_/acid.matkelly.com/')
        res = res.follow()
        assert '"en"' in res.text
        assert '"Language:"' in res.text

    def test_locale_cy_replay_banner(self):
        res = self.testapp.get('/cy/pywb-no-locks/mp_/acid.matkelly.com/')
        res = res.follow()
        assert '"cy"' in res.text
        assert '"Iaith:"' in res.text


