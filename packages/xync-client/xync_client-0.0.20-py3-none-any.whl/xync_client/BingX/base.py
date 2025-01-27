import os
import subprocess
from datetime import datetime
from json import dumps
from uuid import uuid4

from xync_client.Abc.Base import BaseClient


class BaseBingXClient(BaseClient):
    def _prehook(self, _payload: dict = None):
        traceid = str(uuid4()).replace("-", "")
        now = str(int(datetime.now().timestamp() * 1000))
        payload = dumps(_payload, separators=(",", ":"), sort_keys=True) if _payload else "{}"
        prefs = {
            "tests": "../xync_client/BingX/",
            "xync_client": "BingX/",
        }
        pref = prefs.get(os.getcwd().split("/")[-1], "xync_client/BingX/")
        p = subprocess.Popen(["node", pref + "req.mjs", now, traceid, payload], stdout=subprocess.PIPE)
        sign = p.stdout.read().decode().strip()
        return {
            "sign": sign,
            "timestamp": now,
            "traceid": traceid,
        }
