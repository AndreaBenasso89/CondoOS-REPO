"""Channel adapters (anti-corruption layer). Inbound normalization only."""

from condominioos.channels.adapters import ADAPTERS, ChannelAdapter, EmailAdapter, WhatsAppAdapter

__all__ = ["ChannelAdapter", "WhatsAppAdapter", "EmailAdapter", "ADAPTERS"]
