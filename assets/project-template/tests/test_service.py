from __future__ import annotations

import shutil
import unittest
import uuid
from pathlib import Path

from yanbao_runtime.contracts import DeliveryReceipt, InboundMessage, TurnProposal
from yanbao_runtime.service import RuntimeService
from yanbao_runtime.store import StateStore


class FakeModel:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = 0

    async def generate(self, message):
        self.calls += 1
        if self.fail:
            raise RuntimeError("model failed")
        return TurnProposal("reply", ("shared",))


class FakeChannel:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    async def send_text(self, chat_id, text, idempotency_key):
        self.calls.append((chat_id, text, idempotency_key))
        if self.fail:
            raise RuntimeError("channel failed")
        return DeliveryReceipt("provider-1", idempotency_key)


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1] / ".test-tmp" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.database = self.root / "state.sqlite3"
        self.store = StateStore(self.database)
        self.store.initialize()
        self.store.ingest(InboundMessage("m1", "chat", "owner", "text", "hello"))

    def tearDown(self):
        self.store.close()
        shutil.rmtree(self.root, ignore_errors=True)

    async def test_disarmed_never_calls_adapters(self):
        model, channel = FakeModel(), FakeChannel()
        service = RuntimeService(self.store, model, channel)
        self.assertFalse(await service.process_one())
        self.assertEqual(model.calls, 0)
        self.assertEqual(channel.calls, [])

    async def test_armed_stages_then_delivers_and_commits(self):
        self.store.set_armed(True)
        model, channel = FakeModel(), FakeChannel()
        service = RuntimeService(self.store, model, channel)
        self.assertTrue(await service.process_one())
        self.assertEqual(self.store.counts()["events"], 0)
        self.assertTrue(await service.process_one())
        self.assertEqual(self.store.counts()["events"], 1)
        self.assertEqual(len(channel.calls), 1)

    async def test_model_failure_commits_nothing(self):
        self.store.set_armed(True)
        service = RuntimeService(self.store, FakeModel(fail=True), FakeChannel())
        self.assertTrue(await service.process_one())
        self.assertEqual(self.store.counts()["outbox"], 0)
        self.assertEqual(self.store.counts()["events"], 0)

    async def test_channel_failure_preserves_idempotency(self):
        self.store.set_armed(True)
        channel = FakeChannel(fail=True)
        service = RuntimeService(self.store, FakeModel(), channel)
        await service.process_one()
        await service.process_one()
        first_key = channel.calls[0][2]
        self.store.close()

        reopened = StateStore(self.database)
        reopened.initialize()
        reopened.recover()
        self.store = reopened
        good = FakeChannel()
        service = RuntimeService(self.store, FakeModel(), good)
        await service.process_one()
        self.assertEqual(first_key, good.calls[0][2])
        self.assertEqual(self.store.counts()["events"], 1)


if __name__ == "__main__":
    unittest.main()

