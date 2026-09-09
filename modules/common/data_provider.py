"""Shared data layer stub for the public demo build. The real dynamic feed
client (live match data, formations, odds) lives only in the private
commercial product. This stub always reports 'no live overlay available',
which is the same behavior the real client falls back to on any network
error — callers don't need to branch on which build they're running."""


def is_overlay_real(feed):
    """Distinguishes a genuinely fetched dynamic feed from the empty
    placeholder fallback. In the public demo build there is never a real
    feed, so this always returns False."""
    return False


def get_dynamic_overlay(client=None):
    """Public demo build has no dynamic feed client. Always returns None,
    which callers must interpret as 'no live data available'."""
    return None
