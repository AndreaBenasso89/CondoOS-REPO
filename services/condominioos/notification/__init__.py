"""Notification Engine — the sole, verdict-gated egress to channels."""

from condominioos.notification.engine import (
    ChannelClient,
    MockChannelClient,
    NotificationEngine,
    UnauthorizedSendError,
)

__all__ = ["NotificationEngine", "ChannelClient", "MockChannelClient", "UnauthorizedSendError"]
