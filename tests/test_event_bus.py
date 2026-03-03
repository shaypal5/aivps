from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aivp.bus import (
    ACK_ACKED,
    ACK_NACKED,
    ACK_PENDING,
    EVENT_ENVELOPE_VERSION,
    DuplicateEventError,
    EventEnvelope,
    InvalidAckStateError,
    SqliteEventBus,
)


class SqliteEventBusTests(unittest.TestCase):
    def test_publish_persists_event_with_v1_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3"
            bus = SqliteEventBus(db_path)
            envelope = EventEnvelope(
                event_type="sensor.email.received",
                event_source="gmail.sensor",
                payload={"message_id": "m-123", "labels": ["Inbox"]},
            )

            persisted = bus.publish(envelope)
            reloaded = SqliteEventBus(db_path).get_event(envelope.event_id)

            self.assertEqual(persisted.event_id, envelope.event_id)
            self.assertEqual(persisted.envelope_version, EVENT_ENVELOPE_VERSION)
            self.assertEqual(persisted.ack_state, ACK_PENDING)
            self.assertIsNotNone(reloaded)
            assert reloaded is not None
            self.assertEqual(reloaded.event_id, envelope.event_id)
            self.assertEqual(reloaded.envelope_version, EVENT_ENVELOPE_VERSION)
            self.assertEqual(reloaded.payload["message_id"], "m-123")

    def test_publish_rejects_duplicate_event_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3"
            bus = SqliteEventBus(db_path)
            envelope = EventEnvelope(
                event_id="evt-fixed",
                event_type="trigger.schedule",
                event_source="scheduler",
                payload={"agent_id": "vp-expenses"},
            )

            bus.publish(envelope)

            with self.assertRaises(DuplicateEventError):
                bus.publish(envelope)

    def test_ack_state_model_transitions_from_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3"
            bus = SqliteEventBus(db_path)

            first = bus.publish(
                EventEnvelope(
                    event_type="trigger.schedule",
                    event_source="scheduler",
                    payload={"agent_id": "vp-a"},
                )
            )
            second = bus.publish(
                EventEnvelope(
                    event_type="trigger.schedule",
                    event_source="scheduler",
                    payload={"agent_id": "vp-b"},
                )
            )

            self.assertEqual(len(bus.list_pending()), 2)
            self.assertTrue(bus.acknowledge(first.event_id, ACK_ACKED))
            self.assertTrue(bus.acknowledge(first.event_id, ACK_ACKED))
            self.assertTrue(bus.acknowledge(second.event_id, ACK_NACKED))

            first_after = bus.get_event(first.event_id)
            second_after = bus.get_event(second.event_id)
            self.assertIsNotNone(first_after)
            self.assertIsNotNone(second_after)
            assert first_after is not None
            assert second_after is not None
            self.assertEqual(first_after.ack_state, ACK_ACKED)
            self.assertEqual(second_after.ack_state, ACK_NACKED)
            self.assertEqual(len(bus.list_pending()), 0)

    def test_acknowledge_unknown_event_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bus = SqliteEventBus(Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3")

            self.assertFalse(bus.acknowledge("does-not-exist", ACK_ACKED))

    def test_acknowledge_rejects_invalid_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bus = SqliteEventBus(Path(tmpdir) / "runtime" / "db" / "aivp.sqlite3")
            event = bus.publish(
                EventEnvelope(
                    event_type="trigger.schedule",
                    event_source="scheduler",
                    payload={"agent_id": "vp-c"},
                )
            )

            with self.assertRaises(InvalidAckStateError):
                bus.acknowledge(event.event_id, ACK_PENDING)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
