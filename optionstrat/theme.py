"""Design system for the Streamlit OptionStrat app.

Colors, radii and type scale are ported 1:1 (HSL -> hex) from the reference
web app's `src/index.css` design tokens, so the two clients stay visually in
sync even though Streamlit can't run the same Tailwind/shadcn stack.
"""

from __future__ import annotations

from string import Template
from typing import Iterable, Literal

import streamlit as st

Tone = Literal["primary", "accent", "muted", "destructive"]

# ---------------------------------------------------------------------------
# Palette (source of truth: web app's :root HSL tokens)
# ---------------------------------------------------------------------------

BACKGROUND = "#0c1018"
FOREGROUND = "#f8fafc"

CARD = "#121826"
CARD_FOREGROUND = "#f8fafc"
BORDER = "#1f2a3d"

PRIMARY = "#10b77f"
PRIMARY_FOREGROUND = "#0c1018"

SECONDARY = "#1d283a"
SECONDARY_FOREGROUND = "#f8fafc"

MUTED = "#1d283a"
MUTED_FOREGROUND = "#8fa2bc"

ACCENT = "#0da2e7"
ACCENT_FOREGROUND = "#f8fafc"

DESTRUCTIVE = "#ef4343"
DESTRUCTIVE_FOREGROUND = "#f8fafc"

RADIUS_SM = "10px"
RADIUS_MD = "12px"
RADIUS_LG = "14px"
RADIUS_XL = "18px"
RADIUS_2XL = "20px"

_TONE_COLORS: dict[Tone, tuple[str, str]] = {
    "primary": (PRIMARY, PRIMARY_FOREGROUND),
    "accent": (ACCENT, ACCENT_FOREGROUND),
    "muted": (MUTED, FOREGROUND),
    "destructive": (DESTRUCTIVE, DESTRUCTIVE_FOREGROUND),
}


def rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def tone_color(tone: Tone) -> str:
    return _TONE_COLORS[tone][0]


# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

_CSS = Template(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --os-background: $background;
  --os-foreground: $foreground;
  --os-card: $card;
  --os-border: $border;
  --os-primary: $primary;
  --os-primary-foreground: $primary_foreground;
  --os-secondary: $secondary;
  --os-muted: $muted;
  --os-muted-foreground: $muted_foreground;
  --os-accent: $accent;
  --os-destructive: $destructive;
  --os-destructive-foreground: $destructive_foreground;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Inter', system-ui, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background: var(--os-background);
}

[data-testid="stHeader"] {
  background: var(--os-background);
}

[data-testid="stSidebar"] {
  background: $card;
  border-right: 1px solid var(--os-border);
}

[data-testid="stSidebar"] > div {
  padding-top: 1.25rem;
}

/* Make the whole app read tighter / denser, closer to the mobile app */
.main .block-container {
  padding-top: 2rem;
  max-width: 760px;
}

h1, h2, h3, h4 {
  font-family: 'Inter', system-ui, sans-serif !important;
  letter-spacing: -0.02em;
  color: var(--os-foreground) !important;
}

p, span, label, div {
  letter-spacing: -0.01em;
}

hr {
  border-color: var(--os-border) !important;
}

/* Captions / muted text */
[data-testid="stCaptionContainer"], .os-muted {
  color: var(--os-muted-foreground) !important;
}

/* ---------------- Buttons ---------------- */
[data-testid="stButton"] button {
  border-radius: $radius_sm;
  font-weight: 600;
  transition: opacity 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
}

[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
  background: var(--os-primary);
  color: var(--os-primary-foreground);
  border: 1px solid var(--os-primary);
}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
  opacity: 0.88;
}

[data-testid="stButton"] button[kind="secondary"] {
  background: var(--os-card);
  color: var(--os-foreground);
  border: 1px solid var(--os-border);
  border-radius: 999px;
  padding: 0.25rem 1rem;
  font-size: 0.8rem;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
  background: var(--os-muted);
  border-color: var(--os-muted-foreground);
  color: var(--os-foreground);
}

/* ---------------- Inputs ---------------- */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  background: var(--os-secondary);
  color: var(--os-foreground);
  border: 1px solid var(--os-border);
  border-radius: $radius_sm;
}
[data-testid="stTextInput"] input::placeholder {
  color: var(--os-muted-foreground);
}

[data-testid="stForm"] {
  background: var(--os-card);
  border: 1px solid var(--os-border);
  border-radius: $radius_xl;
  padding: 1.1rem 1.1rem 0.6rem 1.1rem;
}

[data-baseweb="select"] > div {
  background: var(--os-secondary) !important;
  border-color: var(--os-border) !important;
  border-radius: $radius_sm !important;
  color: var(--os-foreground) !important;
}

/* Segmented control */
[data-testid="stSegmentedControl"] label {
  background: var(--os-secondary) !important;
  border-color: var(--os-border) !important;
}

/* ---------------- Sidebar nav radio ---------------- */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  border-radius: $radius_sm;
  padding: 0.4rem 0.6rem;
  margin-bottom: 0.1rem;
  transition: background-color 0.15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: var(--os-muted);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: $primary_soft;
}

/* ---------------- Expander ---------------- */
[data-testid="stExpander"] {
  background: var(--os-card);
  border: 1px solid var(--os-border) !important;
  border-radius: $radius_xl !important;
  overflow: hidden;
}

/* ---------------- Tabs ---------------- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0.25rem;
  border-bottom: 1px solid var(--os-border);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  color: var(--os-muted-foreground);
  font-weight: 600;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--os-primary) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  background-color: var(--os-primary) !important;
}

/* ---------------- Dataframe ---------------- */
[data-testid="stDataFrame"] {
  border: 1px solid var(--os-border);
  border-radius: $radius_md;
  overflow: hidden;
}

/* ---------------- Alerts ---------------- */
[data-testid="stAlertContentInfo"] { color: var(--os-foreground); }
[data-testid="stAlert"] {
  border-radius: $radius_lg;
}

/* ---------------- Custom card system ---------------- */
.os-card {
  background: var(--os-card);
  border: 1px solid var(--os-border);
  border-radius: $radius_xl;
  padding: 1rem;
  margin-bottom: 0.85rem;
}
.os-card--tight { padding: 0.85rem; }
.os-card--primary { border-color: $primary_border; }
.os-card--accent { border-color: $accent_border; }
.os-card--destructive { border-color: $destructive_border; }

.os-header-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.9rem;
}
.os-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--os-primary);
  flex-shrink: 0;
}
.os-app-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--os-foreground);
  flex: 1;
  letter-spacing: -0.02em;
}

.os-badge {
  display: inline-block;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.os-section-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--os-muted-foreground);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 1.1rem 0 0.5rem 0;
}
.os-section-title svg { flex-shrink: 0; }

.os-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.os-row + .os-row { margin-top: 0.6rem; }

.os-stat-grid {
  display: grid;
  gap: 0.5rem;
  padding: 0.6rem 0;
  border-top: 1px solid var(--os-border);
  border-bottom: 1px solid var(--os-border);
  margin: 0.6rem 0;
}
.os-stat {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.os-stat-value {
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--os-foreground);
}
.os-stat-label {
  font-size: 0.68rem;
  color: var(--os-muted-foreground);
}

.os-ticker {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--os-foreground);
  letter-spacing: -0.02em;
}
.os-company {
  font-size: 0.72rem;
  color: var(--os-muted-foreground);
  margin-top: -2px;
}
.os-price {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--os-foreground);
}
.os-change-up { color: var(--os-primary); font-weight: 700; font-size: 0.85rem; }
.os-change-down { color: var(--os-destructive); font-weight: 700; font-size: 0.85rem; }

.os-rationale {
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--os-foreground);
}

.os-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.6rem;
  padding: 2.2rem 1rem;
}
.os-empty-state h3 { margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--os-foreground); }
.os-empty-state p { margin: 0; font-size: 0.82rem; color: var(--os-muted-foreground); max-width: 320px; line-height: 1.5; }

.os-spinner {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  border: 3px solid $primary_border;
  border-top-color: var(--os-primary);
  animation: os-spin 0.7s linear infinite;
}
@keyframes os-spin { to { transform: rotate(360deg); } }

.os-chip-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.4rem 0 0.2rem 0; }

/* Hide the little "Press Enter to apply" helper for a cleaner search feel */
[data-testid="InputInstructions"] { opacity: 0.6; }
</style>
"""
)


def inject_theme() -> None:
    st.markdown(
        _CSS.substitute(
            background=BACKGROUND,
            foreground=FOREGROUND,
            card=CARD,
            border=BORDER,
            primary=PRIMARY,
            primary_foreground=PRIMARY_FOREGROUND,
            secondary=SECONDARY,
            muted=MUTED,
            muted_foreground=MUTED_FOREGROUND,
            accent=ACCENT,
            destructive=DESTRUCTIVE,
            destructive_foreground=DESTRUCTIVE_FOREGROUND,
            radius_sm=RADIUS_SM,
            radius_md=RADIUS_MD,
            radius_lg=RADIUS_LG,
            radius_xl=RADIUS_XL,
            primary_soft=rgba(PRIMARY, 0.16),
            primary_border=rgba(PRIMARY, 0.4),
            accent_border=rgba(ACCENT, 0.4),
            destructive_border=rgba(DESTRUCTIVE, 0.35),
        ),
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Small inline icon set (hand-drawn, outline style - not copied from any
# third-party icon library) so section titles get a bit of visual texture.
# ---------------------------------------------------------------------------

def _svg(inner: str) -> str:
    return (
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
        f'stroke-linejoin="round">{inner}</svg>'
    )


ICONS = {
    "star": _svg('<path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7-5.4-4.7 7.1-.6z"/>'),
    "dollar": _svg('<path d="M12 2v20M17 6.5c0-1.9-2-3-5-3s-5 1.3-5 3.2c0 4 10 2 10 6 0 2-2.2 3.3-5 3.3s-5-1.1-5-3"/>'),
    "activity": _svg('<path d="M3 12h4l2 8 4-16 2 8h6"/>'),
    "layers": _svg('<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>'),
    "git": _svg('<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="12" r="2.5"/><path d="M6 8.5V15.5M8.3 12H15.7"/>'),
    "file": _svg('<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/>'),
}


def icon(name: str) -> str:
    return ICONS.get(name, "")


# ---------------------------------------------------------------------------
# Reusable HTML component builders
# ---------------------------------------------------------------------------

def header(title: str = "OptionStrat") -> None:
    st.markdown(
        f'<div class="os-header-row"><div class="os-dot"></div>'
        f'<div class="os-app-title">{title}</div></div>',
        unsafe_allow_html=True,
    )


def section_title(label: str, icon_name: str | None = None) -> None:
    ico = f'<span>{icon(icon_name)}</span>' if icon_name else ""
    st.markdown(
        f'<div class="os-section-title">{ico}<span>{label}</span></div>',
        unsafe_allow_html=True,
    )


def badge(label: str, tone: Tone = "primary") -> str:
    bg, fg = _TONE_COLORS[tone]
    return f'<span class="os-badge" style="background:{bg};color:{fg};">{label}</span>'


def stat_html(label: str, value: str, tone: Tone | None = None, align: str = "left") -> str:
    color = f"color:{tone_color(tone)};" if tone else ""
    items = "flex-end" if align == "right" else "flex-start"
    return (
        f'<div class="os-stat" style="align-items:{items};">'
        f'<span class="os-stat-value" style="{color}">{value}</span>'
        f'<span class="os-stat-label">{label}</span></div>'
    )


def stat_grid(stats: Iterable[tuple[str, str]] | Iterable[tuple[str, str, Tone]]) -> str:
    cells = []
    for entry in stats:
        if len(entry) == 3:
            label, value, tone = entry
        else:
            label, value = entry
            tone = None
        cells.append(stat_html(label, value, tone))
    cols = len(cells) if cells else 1
    return (
        f'<div class="os-stat-grid" style="grid-template-columns: repeat({cols}, 1fr);">'
        + "".join(cells)
        + "</div>"
    )


def card_open(tone: Tone | None = None, tight: bool = False) -> None:
    classes = "os-card"
    if tight:
        classes += " os-card--tight"
    if tone:
        classes += f" os-card--{tone}"
    st.markdown(f'<div class="{classes}">', unsafe_allow_html=True)


def card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_card(inner_html: str, tone: Tone | None = None, tight: bool = False) -> None:
    classes = "os-card"
    if tight:
        classes += " os-card--tight"
    if tone:
        classes += f" os-card--{tone}"
    st.markdown(f'<div class="{classes}">{inner_html}</div>', unsafe_allow_html=True)


def loading_card(message: str, tone: Tone = "primary") -> None:
    render_card(
        f'<div class="os-empty-state"><div class="os-spinner"></div>'
        f'<p style="margin-top:0.2rem;">{message}</p></div>',
        tone=tone,
    )


def empty_state(title: str, body: str, icon_name: str = "activity") -> None:
    render_card(
        f'<div class="os-empty-state">{icon(icon_name)}'
        f"<h3>{title}</h3><p>{body}</p></div>"
    )
