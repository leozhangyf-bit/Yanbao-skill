from __future__ import annotations

import inspect
import unittest

from yanbao_runtime import contracts
from yanbao_runtime.contracts import ContractError, DeliveryReceipt, InboundMessage, TurnProposal


class ContractTests(unittest.TestCase):
    def test_message_type_is_strict(self):
        with self.assertRaises(ContractError):
            InboundMessage("m1", "c1", "u1", "file", "x")

    def test_turn_mapping_rejects_unknown_fields_and_empty_reply(self):
        with self.assertRaises(ContractError):
            TurnProposal.from_mapping({"reply_text": "ok", "candidate_events": [], "extra": 1})
        with self.assertRaises(ContractError):
            TurnProposal.from_mapping({"reply_text": "", "candidate_events": []})

    def test_receipt_requires_both_identities(self):
        with self.assertRaises(ContractError):
            DeliveryReceipt("", "reply-1")
        with self.assertRaises(ContractError):
            DeliveryReceipt("provider-1", "")

    def test_domain_contracts_have_no_infrastructure_imports(self):
        source = inspect.getsource(contracts)
        self.assertNotIn("import sqlite3", source)
        self.assertNotIn("import subprocess", source)


if __name__ == "__main__":
    unittest.main()

