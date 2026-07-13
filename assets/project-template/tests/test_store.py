from __future__ import annotations

import shutil
import unittest
import uuid
from pathlib import Path

from yanbao_runtime.contracts import DeliveryReceipt, InboundMessage, TurnProposal
from yanbao_runtime.store import StateStore, StoreError


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = Path(__file__).parents[1] / ".test-tmp" / uuid.uuid4().hex
        self.temp.mkdir(parents=True)
        self.database = self.temp / "state.sqlite3"
        self.store = StateStore(self.database)
        self.store.initialize()

    def tearDown(self):
        self.store.close()
        shutil.rmtree(self.temp, ignore_errors=True)

    def message(self, message_id="m1"):
        return InboundMessage(message_id, "chat", "owner", "text", "hello")

    def test_duplicate_inbox_and_disarmed_default(self):
        self.assertEqual(self.store.ingest(self.message()), self.store.ingest(self.message()))
        self.assertFalse(self.store.is_armed())
        self.assertEqual(self.store.counts()["inbox"], 1)

    def test_delivery_receipt_is_canonical_boundary(self):
        inbound_id = self.store.ingest(self.message())
        claimed = self.store.claim_next()
        self.assertEqual(claimed["status"], "processing")
        outbox_id = self.store.stage(inbound_id, TurnProposal("reply", ("shared fact",)))
        self.assertEqual(self.store.counts()["events"], 0)
        outbox = self.store.claim_outbox()
        self.store.commit_delivery(
            outbox_id, DeliveryReceipt("provider-message", outbox["idempotency_key"])
        )
        self.assertEqual(self.store.counts()["events"], 1)
        self.assertIsNone(self.store.claim_outbox())

    def test_recovery_keeps_idempotency_and_does_not_duplicate(self):
        inbound_id = self.store.ingest(self.message())
        self.store.claim_next()
        self.store.stage(inbound_id, TurnProposal("reply", ()))
        first = self.store.claim_outbox()
        self.store.close()

        reopened = StateStore(self.database)
        reopened.initialize()
        reopened.recover()
        second = reopened.claim_outbox()
        self.assertEqual(first["idempotency_key"], second["idempotency_key"])
        reopened.close()
        self.store = StateStore(self.database)

    def test_stale_media_transition_raises(self):
        with self.store.connection:
            self.store.connection.execute(
                "INSERT INTO media_jobs(id,direction,status,idempotency_key) VALUES('j1','outbound','planned','media-j1')"
            )
        with self.assertRaises(StoreError):
            self.store.transition_media("j1", "generated", "uploaded")

    def test_backup_is_integral(self):
        target = self.temp / "backup.sqlite3"
        self.assertEqual(self.store.backup(target), target)
        check = StateStore(target)
        self.assertEqual(check.integrity(), "ok")
        check.close()


if __name__ == "__main__":
    unittest.main()
