"""Central reversible free-launch access policy.

The flag is server-only. It never grants organisation, cohort, creator,
staff, or administrative permissions.
"""
import os


def free_access_mode_enabled() -> bool:
    """Return whether the temporary individual-learner free launch is enabled."""
    return os.getenv("FREE_ACCESS_MODE", "false").strip().lower() in {
        "1", "true", "yes", "on",
    }


def is_individual_learner(role: str | None, account_type: str | None) -> bool:
    """Restrict free launch to verified global learner account classes."""
    return (
        str(account_type or "").strip().lower() == "learner"
        and str(role or "").strip().lower() in {"normal", "witstart"}
    )
