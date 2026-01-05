# kafka_producer.py
import json
import time

# Make Kafka optional: if a broker isn't available or kafka-python isn't installed,
# fall back to a no-op logger so the backend can run without Docker/Kafka.
TOPIC = "call_events"

try:
    from kafka import KafkaProducer

    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5
    )

    def send_event(event_type: str, provider_id: int, provider_name: str, extra: dict=None):
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event_type,
            "provider_id": provider_id,
            "provider_name": provider_name,
        }
        if extra:
            payload.update(extra)
        try:
            producer.send(TOPIC, value=payload)
            producer.flush()
        except Exception:
            print("[kafka_producer] failed to send, payload=", payload)
except Exception:
    # kafka-python not installed or broker unreachable at import time
    def send_event(event_type: str, provider_id: int, provider_name: str, extra: dict=None):
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event_type,
            "provider_id": provider_id,
            "provider_name": provider_name,
        }
        if extra:
            payload.update(extra)
        print("[kafka_producer] kafka unavailable — event:", json.dumps(payload))
