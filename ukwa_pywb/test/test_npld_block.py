import subprocess
import requests
import os
import time

TEST_CWD = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "integration-test")

class TestNPLDBlockPage:
    @classmethod
    def setup_class(cls):
        subprocess.run(["docker-compose", "-f", "./docker-compose-test-acl.yml", "build"], cwd=TEST_CWD)
        cls.proc = subprocess.Popen(["docker-compose", "-f", "./docker-compose-test-acl.yml", "up"], cwd=TEST_CWD)
        time.sleep(5)

    @classmethod
    def teardown_class(cls):
        cls.proc.terminate()

    def test_blocked_no_date(self):
        resp = requests.get("http://localhost:8100/reading-room/https://idpf.github.io/epub3-samples/30/samples.html")
        assert resp.status_code == 451

        assert "npld-viewer://reading-room/https://idpf.github.io/epub3-samples/30/samples.html" in resp.text

    def test_blocked_with_date(self):
        resp = requests.get("http://localhost:8100/reading-room/20220908/https://idpf.github.io/epub3-samples/30/samples.html")
        assert resp.status_code == 451

        assert "npld-viewer://reading-room/20220908/https://idpf.github.io/epub3-samples/30/samples.html" in resp.text

    def test_blocked_incorrect_header(self):
        resp = requests.get("http://localhost:8100/reading-room/20220908mp_/https://idpf.github.io/epub3-samples/30/samples.html",
            headers={"X-NPLD-Player-Auth-Token": "auth-value-3"})

        assert resp.status_code == 451

        assert "npld-viewer://reading-room/20220908mp_/https://idpf.github.io/epub3-samples/30/samples.html" in resp.text

    def test_allowed_correct_header(self):
        resp = requests.get("http://localhost:8100/reading-room/20220908/https://idpf.github.io/epub3-samples/30/samples.html",
            headers={"X-NPLD-Player-Auth-Token": "auth-value-1"})

        assert resp.status_code == 200

        resp = requests.get("http://localhost:8100/reading-room/20220908mp_/https://idpf.github.io/epub3-samples/30/samples.html",
            headers={"X-NPLD-Player-Auth-Token": "auth-value-1"})

        assert resp.status_code == 200

    def test_single_use_lock(self):
        resp = requests.get("http://localhost:8100/reading-room/20220908mp_/https://idpf.github.io/epub3-samples/30/samples.html",
            headers={"X-NPLD-Player-Auth-Token": "auth-value-1"})

        assert resp.status_code == 403


