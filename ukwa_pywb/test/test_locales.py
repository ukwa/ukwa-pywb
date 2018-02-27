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

        assert "System Mynediad Archif Gwe'r DU" in res.text

    def test_locale_en_replay_banner(self):
        res = self.testapp.get('/en/pywb-no-locks/mp_/acid.matkelly.com/')
        res = res.follow()
        assert '"en"' in res.text
        assert '"Archived On:"' in res.text

    def test_locale_cy_replay_banner(self):
        res = self.testapp.get('/cy/pywb-no-locks/mp_/acid.matkelly.com/')
        res = res.follow()
        assert '"cy"' in res.text
        assert '"Archif Ar:"' in res.text


