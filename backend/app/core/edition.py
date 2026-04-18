"""
Edition feature gate system (Desktop Mode)
"""
from enum import Enum


class Feature(str, Enum):
    """All features that can be gated by edition."""
    # Community features
    WORKFLOW_CREATE = "workflow_create"
    WORKFLOW_EXECUTE = "workflow_execute"
    PYTHON_NODE = "python_node"
    HTTP_NODE = "http_node"
    CONDITION_NODE = "condition_node"
    LOOP_NODE = "loop_node"
    DELAY_NODE = "delay_node"

    # Enterprise features
    CRON_SCHEDULE = "cron_schedule"
    PARALLEL_EXECUTION = "parallel_execution"
    API_TRIGGER = "api_trigger"
    RBAC_MANAGEMENT = "rbac_management"
    AUDIT_LOG = "audit_log"
    DOCKER_SANDBOX = "docker_sandbox"
    UNLIMITED_WORKFLOWS = "unlimited_workflows"


# Feature -> minimum required edition (as string for SQLite)
FEATURE_EDITION_MAP: dict[Feature, str] = {
    # Community
    Feature.WORKFLOW_CREATE: "community",
    Feature.WORKFLOW_EXECUTE: "community",
    Feature.PYTHON_NODE: "community",
    Feature.HTTP_NODE: "community",
    Feature.CONDITION_NODE: "community",
    Feature.LOOP_NODE: "community",
    Feature.DELAY_NODE: "community",
    # Enterprise
    Feature.CRON_SCHEDULE: "enterprise",
    Feature.PARALLEL_EXECUTION: "enterprise",
    Feature.API_TRIGGER: "enterprise",
    Feature.RBAC_MANAGEMENT: "enterprise",
    Feature.AUDIT_LOG: "enterprise",
    Feature.DOCKER_SANDBOX: "enterprise",
    Feature.UNLIMITED_WORKFLOWS: "enterprise",
}

# Edition hierarchy for comparison
EDITION_HIERARCHY = {
    "community": 0,
    "enterprise": 1,
}


def check_feature_access(user_edition: str, feature: Feature) -> bool:
    """Check if a user's edition has access to a specific feature."""
    required = FEATURE_EDITION_MAP.get(feature)
    if required is None:
        return True
    user_level = EDITION_HIERARCHY.get(user_edition, 0)
    required_level = EDITION_HIERARCHY.get(required, 0)
    return user_level >= required_level


def get_available_features(edition: str) -> list[Feature]:
    """Get all features available for a given edition."""
    edition_level = EDITION_HIERARCHY.get(edition, 0)
    return [
        feature for feature, required_edition in FEATURE_EDITION_MAP.items()
        if edition_level >= EDITION_HIERARCHY.get(required_edition, 0)
    ]


def get_edition_limits(edition: str) -> dict:
    """Get resource limits for a given edition."""
    from app.config import settings
    if edition == "community":
        return {
            "max_workflows": settings.COMMUNITY_MAX_WORKFLOWS,
            "max_concurrent_tasks": 1,
            "sandbox_timeout": settings.SANDBOX_TIMEOUT_SECONDS,
        }
    else:
        return {
            "max_workflows": -1,  # unlimited
            "max_concurrent_tasks": 10,
            "sandbox_timeout": settings.SANDBOX_TIMEOUT_SECONDS * 4,
        }
