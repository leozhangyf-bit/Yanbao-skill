from __future__ import annotations

import contextlib
import io
import json
import shutil
import unittest
import uuid
from pathlib import Path

from yanbao_runtime.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1] / ".test-tmp" / uuid.uuid4().hex
        self.root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def call(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--project-root", str(self.root), *args])
        return code, json.loads(output.getvalue())

    def test_init_and_status_are_disarmed_and_path_free(self):
        self.assertEqual(self.call("init")[0], 0)
        code, status = self.call("status")
        self.assertEqual(code, 0)
        self.assertFalse(status["armed"])
        self.assertNotIn(str(self.root), json.dumps(status))

    def test_arm_and_disarm_require_exact_confirmation(self):
        self.call("init")
        with self.assertRaises(SystemExit):
            main(["--project-root", str(self.root), "arm", "--confirm", "wrong"])
        self.assertTrue(self.call("arm", "--confirm", "ARM-YANBAO")[1]["armed"])
        self.assertFalse(self.call("disarm", "--confirm", "DISARM-YANBAO")[1]["armed"])

    def test_backup_and_restore_check(self):
        self.call("init")
        self.assertTrue(self.call("backup")[1]["backup_created"])
        backup = next((self.root / "data" / "backups").glob("*.sqlite3"))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--project-root", str(self.root), "restore-check", str(backup)])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())["database_integrity"])

    def test_run_refuses_without_real_adapters(self):
        self.call("init")
        with self.assertRaisesRegex(SystemExit, "not configured"):
            main(["--project-root", str(self.root), "run"])


if __name__ == "__main__":
    unittest.main()

