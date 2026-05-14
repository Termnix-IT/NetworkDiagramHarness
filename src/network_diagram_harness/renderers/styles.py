from __future__ import annotations


StyleMap = dict[str, dict[str, str]]
ZoneStyleMap = dict[str, tuple[str, str]]


NODE_STYLE_PROFILES: dict[str, StyleMap] = {
    "default": {
        "database": {"fillcolor": "#fef3c7", "color": "#b45309"},
        "external": {"fillcolor": "#e0f2fe", "color": "#0369a1"},
        "firewall": {"fillcolor": "#fee2e2", "color": "#b91c1c"},
        "load_balancer": {"fillcolor": "#dcfce7", "color": "#15803d"},
        "network": {"fillcolor": "#f1f5f9", "color": "#475569"},
        "server": {"fillcolor": "#ede9fe", "color": "#6d28d9"},
        "subnet": {"fillcolor": "#ecfeff", "color": "#0e7490"},
    },
    "muted": {
        "database": {"fillcolor": "#f5f5f4", "color": "#78716c"},
        "external": {"fillcolor": "#f8fafc", "color": "#64748b"},
        "firewall": {"fillcolor": "#fafafa", "color": "#737373"},
        "load_balancer": {"fillcolor": "#f0fdf4", "color": "#65a30d"},
        "network": {"fillcolor": "#f8fafc", "color": "#64748b"},
        "server": {"fillcolor": "#f5f3ff", "color": "#7c3aed"},
        "subnet": {"fillcolor": "#f0f9ff", "color": "#0284c7"},
    },
    "contrast": {
        "database": {"fillcolor": "#ffedd5", "color": "#9a3412"},
        "external": {"fillcolor": "#dbeafe", "color": "#1d4ed8"},
        "firewall": {"fillcolor": "#fecaca", "color": "#991b1b"},
        "load_balancer": {"fillcolor": "#bbf7d0", "color": "#166534"},
        "network": {"fillcolor": "#e2e8f0", "color": "#334155"},
        "server": {"fillcolor": "#ddd6fe", "color": "#5b21b6"},
        "subnet": {"fillcolor": "#cffafe", "color": "#155e75"},
    },
}


ZONE_STYLE_PROFILES: dict[str, ZoneStyleMap] = {
    "default": {
        "cloud": ("#fefce8", "#ca8a04"),
        "dmz": ("#fff7ed", "#f97316"),
        "edge": ("#fff7ed", "#f97316"),
        "internet": ("#f8fafc", "#94a3b8"),
        "internal": ("#f0fdf4", "#16a34a"),
        "other": ("#f8fafc", "#cbd5e1"),
    },
    "muted": {
        "cloud": ("#fafaf9", "#a8a29e"),
        "dmz": ("#fafafa", "#a3a3a3"),
        "edge": ("#fafafa", "#a3a3a3"),
        "internet": ("#f8fafc", "#cbd5e1"),
        "internal": ("#f7fee7", "#84cc16"),
        "other": ("#f8fafc", "#cbd5e1"),
    },
    "contrast": {
        "cloud": ("#fef9c3", "#a16207"),
        "dmz": ("#fed7aa", "#c2410c"),
        "edge": ("#fed7aa", "#c2410c"),
        "internet": ("#e0f2fe", "#0369a1"),
        "internal": ("#dcfce7", "#15803d"),
        "other": ("#e2e8f0", "#475569"),
    },
}


def normalize_style_profile(profile: str | None) -> str:
    return profile or "default"


def node_style_profile(profile: str | None) -> StyleMap:
    return NODE_STYLE_PROFILES[normalize_style_profile(profile)]


def zone_style_profile(profile: str | None) -> ZoneStyleMap:
    return ZONE_STYLE_PROFILES[normalize_style_profile(profile)]
