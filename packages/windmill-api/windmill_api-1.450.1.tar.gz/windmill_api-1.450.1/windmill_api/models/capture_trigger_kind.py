from enum import Enum


class CaptureTriggerKind(str, Enum):
    EMAIL = "email"
    HTTP = "http"
    KAFKA = "kafka"
    NATS = "nats"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"

    def __str__(self) -> str:
        return str(self.value)
