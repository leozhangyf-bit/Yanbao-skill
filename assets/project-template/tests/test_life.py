from __future__ import annotations

import shutil
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from yanbao_runtime.contracts import (
    ActorUpdate,
    BoundedDeception,
    ContractError,
    DeliveryReceipt,
    LifeAdvanceProposal,
    LifeWake,
    ProactiveIntentProposal,
)
from yanbao_runtime.life import WakePolicy
from yanbao_runtime.service import LifeRuntimeService
from yanbao_runtime.store import StateStore, StoreError


UTC = timezone.utc


class FakeLife:
    def __init__(self, proposal=None):
        self.calls = 0
        self.proposal = proposal

    async def advance(self, request):
        self.calls += 1
        if self.proposal is None:
            raise RuntimeError("unexpected life call")
        return self.proposal


class LifeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1] / ".test-tmp" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.store = StateStore(self.root / "state.sqlite3")
        self.store.initialize()
        self.store.set_armed(True)
        self.start = datetime(2026, 1, 1, 8, tzinfo=UTC)

    def tearDown(self):
        self.store.close()
        shutil.rmtree(self.root, ignore_errors=True)

    def bootstrap(self, *, pressure=0, next_hours=1000, confirmed=True):
        self.store.bootstrap_life(
            "role-1",
            "immutable-v1",
            "Asia/Shanghai",
            [{
                "thread_id": "career",
                "goal": "争取主导下一次重要项目",
                "pressure": pressure,
                "next_decision_at": (self.start + timedelta(hours=next_hours)).isoformat(),
                "allowed_severity": "ordinary",
                "actor_ids": ["colleague"],
            }],
            [{
                "actor_id": "colleague",
                "name": "同事甲",
                "relationship": "合作中带竞争",
                "motivation": "争取同一个项目的主导权",
                "stance": "表面合作",
            }],
            confirmed=confirmed,
        )

    def proposal(self, event_id="event-1", cause_ids=(), contact=False):
        return LifeAdvanceProposal(
            event_id=event_id,
            occurred_at=self.start.isoformat(),
            thread_id="career",
            event_kind="choice",
            severity="ordinary",
            causal_basis="项目截止期临近，同事也在争取主导权",
            role_action="她没有等待用户建议，先提交了自己的方案",
            event_summary="她提前提交方案，迫使同事重新选择合作方式",
            consequence="她获得先手，但也让竞争关系变得更明显",
            actor_ids=("colleague",),
            cause_event_ids=tuple(cause_ids),
            thread_status="active",
            thread_pressure=2,
            next_decision_at=(self.start + timedelta(days=2)).isoformat(),
            disclosure="should_contact" if contact else "private",
            actor_updates=(ActorUpdate(
                "colleague", "开始认真评估她的竞争力", "决定是否提出合作",
                (self.start + timedelta(days=1)).isoformat(),
            ),),
            proactive_intent=(
                ProactiveIntentProposal("她想说这次主动争取的结果", "只讲提交方案和同事反应")
                if contact else None
            ),
        )

    def commit_contact(self, event_id, occurred_at, cause_ids=()):
        wake_id = "wake:" + event_id
        self.store.enqueue_life_wake(
            LifeWake(wake_id, "role-1", occurred_at.isoformat(), "deadline")
        )
        self.store.claim_life_wake(occurred_at.isoformat())
        base = self.proposal(event_id=event_id, cause_ids=cause_ids, contact=True)
        proposal = LifeAdvanceProposal(**{
            **base.__dict__,
            "occurred_at": occurred_at.isoformat(),
            "event_summary": f"{base.event_summary}（{event_id}）",
            "next_decision_at": (occurred_at + timedelta(days=1)).isoformat(),
        })
        self.store.commit_life_advance(wake_id, proposal, "decision_due")
        return "intent:" + event_id

    async def test_sixty_daily_checks_do_not_force_model_calls(self):
        self.bootstrap()
        fake = FakeLife()
        service = LifeRuntimeService(self.store, fake, WakePolicy())
        for day in range(30):
            first = self.start + timedelta(days=day)
            self.store.ensure_daily_wakes(
                "role-1", first.date().isoformat(),
                (first.isoformat(), (first + timedelta(hours=8)).isoformat()),
            )
            await service.process_one(first + timedelta(hours=9))
            await service.process_one(first + timedelta(hours=9))
        self.assertEqual(fake.calls, 0)
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM life_wakes").fetchone()[0], 60
        )

    async def test_due_thread_advances_once_and_commits_private_canon(self):
        self.bootstrap(pressure=4, next_hours=-1)
        wake = LifeWake("wake-1", "role-1", self.start.isoformat(), "deadline")
        self.store.enqueue_life_wake(wake)
        fake = FakeLife(self.proposal())
        service = LifeRuntimeService(self.store, fake)
        self.assertTrue(await service.process_one(self.start))
        self.assertEqual(fake.calls, 1)
        event = self.store.connection.execute("SELECT * FROM life_events").fetchone()
        self.assertEqual(event["canon_status"], "private_committed")
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM life_disclosures").fetchone()[0], 0)

    async def test_long_gap_coalesces_without_daily_backfill(self):
        self.bootstrap()
        for day in range(12):
            moment = self.start + timedelta(days=day)
            self.store.enqueue_life_wake(
                LifeWake(f"gap-{day}", "role-1", moment.isoformat(), "scheduled")
            )
        skipped = self.store.coalesce_overdue_wakes(
            "role-1", (self.start + timedelta(days=20)).isoformat()
        )
        self.assertEqual(skipped, 11)
        self.assertEqual(
            self.store.connection.execute("SELECT count(*) FROM life_wakes WHERE status='pending'").fetchone()[0], 1
        )

    async def test_draft_life_cannot_wake_until_confirmed(self):
        self.bootstrap(confirmed=False)
        with self.assertRaises(StoreError):
            self.store.enqueue_life_wake(
                LifeWake("draft", "role-1", self.start.isoformat(), "scheduled")
            )
        self.store.confirm_life("role-1")
        self.store.enqueue_life_wake(
            LifeWake("confirmed", "role-1", self.start.isoformat(), "scheduled")
        )

    async def test_unknown_actor_and_major_event_are_rejected(self):
        self.bootstrap(pressure=4, next_hours=-1)
        self.store.enqueue_life_wake(
            LifeWake("wake-bad", "role-1", self.start.isoformat(), "deadline")
        )
        row = self.store.claim_life_wake(self.start.isoformat())
        bad = self.proposal()
        bad = LifeAdvanceProposal(**{**bad.__dict__, "actor_ids": ("stranger",)})
        with self.assertRaises(StoreError):
            self.store.commit_life_advance(row["wake_id"], bad, "decision_due")

    async def test_deception_requires_truth_motive_and_exposure_pressure(self):
        with self.assertRaises(ContractError):
            BoundedDeception("truth", "cover", "motive", 0)
        valid = BoundedDeception("她已经提交方案", "她还在考虑", "不想显得太争强", 3)
        self.assertEqual(valid.exposure_pressure, 3)

    async def test_proactive_intent_exists_before_visible_disclosure(self):
        self.bootstrap(pressure=4, next_hours=-1)
        self.store.enqueue_life_wake(
            LifeWake("wake-contact", "role-1", self.start.isoformat(), "deadline")
        )
        fake = FakeLife(self.proposal(contact=True))
        await LifeRuntimeService(self.store, fake).process_one(self.start)
        intent = self.store.connection.execute("SELECT * FROM proactive_intents").fetchone()
        self.assertEqual(intent["status"], "pending")
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM life_disclosures").fetchone()[0], 0)

    async def test_unanswered_contact_requires_new_causal_progress(self):
        self.bootstrap(pressure=4, next_hours=-1)
        first = self.commit_contact("first", self.start)
        first_outbox = self.store.stage_proactive_text(first, "chat", "具体进展")
        claimed = self.store.claim_proactive_outbox()
        self.store.commit_proactive_delivery(
            first_outbox, DeliveryReceipt("provider-1", claimed["idempotency_key"])
        )
        second = self.commit_contact("second", self.start + timedelta(hours=2))
        self.assertIsNone(self.store.stage_proactive_text(second, "chat", "换句话再说一次"))
        row = self.store.connection.execute(
            "SELECT status,suppressed_reason FROM proactive_intents WHERE intent_id=?", (second,)
        ).fetchone()
        self.assertEqual(row["suppressed_reason"], "unanswered_without_material_progress")

    async def test_proactive_delivery_cap_is_two_per_local_day(self):
        self.bootstrap(pressure=4, next_hours=-1)
        previous = ()
        for index in range(2):
            event_id = f"cap-{index}"
            intent = self.commit_contact(event_id, self.start + timedelta(hours=index), previous)
            outbox_id = self.store.stage_proactive_text(intent, "chat", f"进展 {index}")
            claimed = self.store.claim_proactive_outbox()
            self.store.commit_proactive_delivery(
                outbox_id, DeliveryReceipt(f"provider-{index}", claimed["idempotency_key"])
            )
            self.store.note_user_activity("role-1")
            previous = (event_id,)
        third = self.commit_contact("cap-2", self.start + timedelta(hours=2), previous)
        self.assertIsNone(self.store.stage_proactive_text(third, "chat", "第三条"))
        row = self.store.connection.execute(
            "SELECT suppressed_reason FROM proactive_intents WHERE intent_id=?", (third,)
        ).fetchone()
        self.assertEqual(row["suppressed_reason"], "daily_limit")

    async def test_three_neutral_worldlines_stay_isolated_without_external_stimuli(self):
        seeds = (
            ("curator", "争取独立策展机会", "mentor"),
            ("engineer", "完成一次关键系统改造", "reviewer"),
            ("student", "赢得成年组研究竞赛", "teammate"),
        )
        for index, (role_id, goal, actor_id) in enumerate(seeds):
            self.store.bootstrap_life(
                role_id,
                f"invariant-{role_id}",
                "Asia/Shanghai",
                [{
                    "thread_id": f"thread-{role_id}",
                    "goal": goal,
                    "pressure": index,
                    "next_decision_at": (self.start + timedelta(days=40)).isoformat(),
                    "actor_ids": [actor_id],
                }],
                [{
                    "actor_id": actor_id,
                    "name": f"角色-{actor_id}",
                    "relationship": "持续合作关系",
                    "motivation": f"推动 {goal}",
                    "stance": "观察下一步行动",
                }],
                confirmed=True,
            )
            self.store.enqueue_life_wake(
                LifeWake(f"wake-{role_id}", role_id, self.start.isoformat(), "scheduled")
            )
        requests = []
        for _ in seeds:
            row = self.store.claim_life_wake(self.start.isoformat())
            request = self.store.life_request(row)
            requests.append(request)
            self.store.skip_life_wake(row["wake_id"], "test_inspection")
        self.assertEqual({request.wake.role_id for request in requests}, {seed[0] for seed in seeds})
        for request in requests:
            self.assertEqual(len(request.threads), 1)
            self.assertEqual(len(request.actors), 1)
            self.assertEqual(request.external_stimuli, ())
            self.assertIn(request.wake.role_id, request.threads[0].thread_id)


if __name__ == "__main__":
    unittest.main()
