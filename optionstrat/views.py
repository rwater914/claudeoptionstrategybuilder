from __future__ import annotations

from typing import Any, Iterable

import pandas as pd
import streamlit as st

from . import theme
from .models import Analysis, IndexPicks, MarketItem, VixPredictor

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def money(value: Any) -> str:
    return f"${float(value):,.2f}" if value is not None else "—"


def percent(value: Any, fraction: bool = True) -> str:
    if value is None:
        return "—"
    number = float(value) * (100 if fraction else 1)
    return f"{number:.1f}%"


def signed_money(value: Any) -> str:
    if value is None:
        return "—"
    number = float(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}${abs(number):.2f}"


def dict_rows(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in item.items() if value is not None} for item in items]


def strategy_tone(strategy: str | None) -> theme.Tone:
    label = (strategy or "").lower()
    if "condor" in label:
        return "accent"
    if "weekend" in label:
        return "destructive"
    if "small" in label or "account" in label:
        return "muted"
    return "primary"


# ---------------------------------------------------------------------------
# Generic pick / market item card
# ---------------------------------------------------------------------------


def render_market_item(item: MarketItem, badge_label: str | None = None) -> None:
    strategy = item.strategy or "Bull put spread"
    tone = strategy_tone(strategy)
    details = item.model_dump(exclude_none=True)
    core_keys = {
        "ticker", "companyName", "spotPrice", "strategy", "dte",
        "probabilityOfProfit", "rationale", "expirationDate",
    }
    credit = details.get("creditEstimate", details.get("netPremium"))
    max_loss = details.get("maxLoss")

    stats: list[tuple] = []
    if credit is not None:
        stats.append(("Credit", money(credit), tone))
    if max_loss is not None:
        stats.append(("Max loss", money(max_loss)))
    if item.probabilityOfProfit is not None:
        stats.append(("POP", percent(item.probabilityOfProfit), tone))

    html = [theme.badge(badge_label or strategy, tone)]
    html.append(
        '<div class="os-row">'
        f'<div><div class="os-ticker">{item.ticker}</div>'
        f'<div class="os-company">{item.companyName or ""}</div></div>'
        '<div style="text-align:right;">'
        f'<div class="os-price" style="font-size:1.05rem;">{money(item.spotPrice)}</div>'
        '<div class="os-stat-label">Spot price</div></div>'
        "</div>"
    )
    if stats:
        html.append(theme.stat_grid(stats))
    footer_bits = []
    if item.dte is not None:
        footer_bits.append(f'<span style="font-weight:600;">{item.dte} DTE</span>')
    if item.expirationDate:
        footer_bits.append(f'<span class="os-stat-label">{item.expirationDate}</span>')
    if footer_bits:
        html.append(
            '<div class="os-row" style="margin-top:0.5rem;">' + "".join(footer_bits) + "</div>"
        )
    if item.rationale:
        html.append(f'<p class="os-rationale" style="margin-top:0.6rem;">{item.rationale}</p>')

    theme.render_card("".join(html), tone=tone)

    for key in core_keys | {"creditEstimate", "netPremium", "maxLoss"}:
        details.pop(key, None)
    if details:
        with st.expander("More details"):
            st.json(details)


# ---------------------------------------------------------------------------
# Analyze page
# ---------------------------------------------------------------------------


def _leg_header(columns: list[str]) -> str:
    cells = "".join(
        f'<span class="os-stat-label" style="font-weight:700;text-transform:uppercase;">{c}</span>'
        for c in columns
    )
    n = len(columns)
    return (
        f'<div style="display:grid;grid-template-columns:repeat({n},1fr);'
        f'padding-bottom:0.4rem;border-bottom:1px solid {theme.BORDER};">'
        + cells
        + "</div>"
    )


def render_analysis(data: Analysis) -> None:
    is_up = data.change >= 0
    change_class = "os-change-up" if is_up else "os-change-down"
    arrow = "▲" if is_up else "▼"
    header_html = (
        '<div class="os-row">'
        f'<div><div class="os-ticker" style="font-size:1.6rem;">{data.ticker}</div>'
        f'<div class="os-company">{data.companyName or ""}</div>'
        '<div style="margin-top:0.5rem;display:flex;align-items:baseline;gap:0.5rem;">'
        f'<span class="os-price">{money(data.spotPrice)}</span>'
        f'<span class="{change_class}">{arrow} {signed_money(data.change)} '
        f'({"+" if is_up else ""}{data.changePercent:.2f}%)</span>'
        "</div></div>"
        '<div style="text-align:right;">'
        '<div class="os-stat-label" style="text-transform:uppercase;">Implied Vol</div>'
        f'<div class="os-price" style="font-size:1.1rem;">{percent(data.impliedVolatility)}</div>'
        "</div></div>"
    )
    theme.render_card(header_html)

    theme.section_title("Rationale", "file")
    theme.render_card(f'<p class="os-rationale">{data.rationale}</p>')

    spread_tab, condor_tab, range_tab = st.tabs(["Bull put spreads", "Iron condors", "Predicted ranges"])

    with spread_tab:
        theme.card_open()
        for i, group in enumerate(data.spreads):
            if i:
                st.markdown(f'<hr style="border-color:{theme.BORDER};margin:0.8rem 0;">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="os-row"><span style="font-weight:700;">{group.get("dte", "—")} DTE</span>'
                f'<span class="os-stat-label">Exp {group.get("expirationDate", "")}</span></div>',
                unsafe_allow_html=True,
            )
            rows_html = [_leg_header(["Δ", "Short / Long", "Credit", "POP"])]
            for leg in group.get("legs", []):
                delta = leg.get("delta")
                delta_txt = f"{delta * 100:.0f}" if delta is not None else "—"
                strikes = f'${leg.get("shortStrike", "—")} / ${leg.get("longStrike", "—")}'
                credit_txt = money(leg.get("creditEstimate"))
                pop_txt = percent(leg.get("probabilityOfProfit"))
                rows_html.append(
                    '<div style="display:grid;grid-template-columns:repeat(4,1fr);padding:0.45rem 0;'
                    f'border-bottom:1px solid {theme.BORDER};align-items:center;font-size:0.8rem;">'
                    f'<span style="font-weight:600;">{delta_txt}</span>'
                    f'<span>{strikes}</span>'
                    f'<span style="color:{theme.PRIMARY};font-weight:700;">{credit_txt}</span>'
                    f'<span>{pop_txt}</span></div>'
                )
            st.markdown("".join(rows_html), unsafe_allow_html=True)
        theme.card_close()

    with condor_tab:
        theme.card_open(tone="accent")
        for i, group in enumerate(data.condors):
            c = group.get("condor", {})
            if i:
                st.markdown(f'<hr style="border-color:{theme.BORDER};margin:0.8rem 0;">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="os-row"><span style="font-weight:700;">{group.get("dte", "—")} DTE</span>'
                f'<span class="os-stat-label">Exp {group.get("expirationDate", "")}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                theme.stat_grid(
                    [
                        ("Put short / long", f'${c.get("shortPutStrike", "—")} / ${c.get("longPutStrike", "—")}'),
                        ("Call short / long", f'${c.get("shortCallStrike", "—")} / ${c.get("longCallStrike", "—")}'),
                    ]
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                theme.stat_grid(
                    [
                        ("Credit", money(c.get("creditEstimate")), "accent"),
                        ("Max loss", money(c.get("maxLoss"))),
                        ("Wings", f'${c.get("putWidth", "—")} / ${c.get("callWidth", "—")}'),
                    ]
                ),
                unsafe_allow_html=True,
            )
        theme.card_close()

    with range_tab:
        theme.card_open()
        cells = []
        for r in data.ranges:
            low = r.get("low")
            high = r.get("high")
            pct = r.get("expectedMovePct")
            pct_txt = f"±{pct:.2f}%" if isinstance(pct, (int, float)) else ""
            cells.append(
                '<div style="background:'
                f'{theme.SECONDARY};border:1px solid {theme.BORDER};border-radius:{theme.RADIUS_MD};'
                'padding:0.75rem;">'
                f'<div class="os-stat-label" style="text-transform:uppercase;font-weight:700;">{r.get("label", "")}</div>'
                '<div style="margin-top:0.3rem;font-weight:700;">'
                f'{money(low)} <span class="os-stat-label">→</span> {money(high)}</div>'
                f'<div class="os-stat-label" style="margin-top:0.2rem;">{pct_txt}</div></div>'
            )
        n_cols = 2 if len(cells) > 1 else 1
        st.markdown(
            f'<div style="display:grid;grid-template-columns:repeat({n_cols},1fr);gap:0.6rem;">'
            + "".join(cells)
            + "</div>",
            unsafe_allow_html=True,
        )
        theme.card_close()


# ---------------------------------------------------------------------------
# Index plays page
# ---------------------------------------------------------------------------


def render_index(data: IndexPicks) -> None:
    snapshot = data.snapshot
    change = snapshot.get("change")
    is_up = (change or 0) >= 0
    change_class = "os-change-up" if is_up else "os-change-down"

    header_html = (
        '<div class="os-row">'
        f'<div><div class="os-ticker">{snapshot.get("index", "")}</div>'
        f'<div class="os-company">{snapshot.get("displayName", "")}</div>'
        '<div style="margin-top:0.5rem;display:flex;align-items:baseline;gap:0.5rem;">'
        f'<span class="os-price">{money(snapshot.get("spotPrice"))}</span>'
        f'<span class="{change_class}">{signed_money(change)} '
        f'({percent(snapshot.get("changePercent"), fraction=False)})</span>'
        "</div></div>"
        '<div style="text-align:right;">'
        f'<span class="os-badge" style="background:{theme.SECONDARY};color:{theme.FOREGROUND};">'
        f'{snapshot.get("marketStatus", "—")}</span></div></div>'
    )
    theme.render_card(header_html)
    theme.render_card(theme.stat_grid([("Implied volatility", percent(snapshot.get("impliedVolatility")))]))

    theme.section_title("DTE picks", "layers")
    for group in data.dtePicks:
        with st.expander(
            f'{group.get("dte", "—")} DTE · {group.get("expirationDate", "")}',
            expanded=group.get("dte") == 0,
        ):
            rows = dict_rows(group.get("picks", []))
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No picks available for this expiration.")

    theme.section_title("Weekend theta setup", "star")
    weekend = data.weekendPlay
    eligible = bool(weekend.get("eligible"))
    tone: theme.Tone = "primary" if eligible else "muted"
    reason = weekend.get(
        "reason",
        "Entry window is open." if eligible else "No weekend setup is available right now.",
    )
    weekend_extra = {k: v for k, v in weekend.items() if k not in {"eligible", "reason"} and v is not None}
    html = [theme.badge("Weekend play" if eligible else "Not eligible", tone)]
    html.append(f'<p class="os-rationale">{reason}</p>')
    theme.render_card("".join(html), tone=tone)
    if weekend_extra:
        with st.expander("Weekend setup details"):
            st.json(weekend_extra)

    theme.section_title("Event risk", "activity")
    risk = data.weekendEventRisk
    status = risk.get("status", "unknown")
    status_tone: theme.Tone = (
        "primary" if status == "clear" else ("destructive" if status in {"blocked", "check_required"} else "muted")
    )
    summary = risk.get("summary", "Event information is limited.")
    theme.render_card(
        theme.badge(status.replace("_", " ").title(), status_tone) + f'<p class="os-rationale">{summary}</p>',
        tone=status_tone,
    )
    events = risk.get("events", [])
    if events:
        theme.card_open()
        st.dataframe(pd.DataFrame(dict_rows(events)), use_container_width=True, hide_index=True)
        theme.card_close()

    with st.expander("Methodology"):
        st.write(data.methodology)


# ---------------------------------------------------------------------------
# VIX predictor page
# ---------------------------------------------------------------------------


def render_vix(data: VixPredictor) -> None:
    fear_color = data.fearColor or theme.MUTED
    spy_up = data.spyChange >= 0
    vix_up = data.vixChange >= 0

    header_html = (
        f'<span class="os-badge" style="background:{fear_color};color:#0c1018;">{data.fearLabel}</span>'
        + theme.stat_grid(
            [
                ("VIX", f"{data.vixLevel:.2f}", "primary" if vix_up else "destructive"),
                ("90-day percentile", f"{data.vixPercentile:.0f}%"),
                ("SPY", money(data.spyPrice), "primary" if spy_up else "destructive"),
            ]
        )
        + f'<p class="os-rationale" style="margin-top:0.6rem;">{data.commentary}</p>'
    )
    theme.render_card(header_html)

    theme.section_title("SPY expected moves", "activity")
    theme.card_open()
    rows = dict_rows(data.expectedMoves)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No expected-move data available.")
    theme.card_close()

    theme.section_title("VIX history", "activity")
    history = pd.DataFrame(dict_rows(data.vixHistory))
    theme.card_open()
    if not history.empty and {"date", "close"}.issubset(history.columns):
        history["date"] = pd.to_datetime(history["date"])
        st.line_chart(history.set_index("date")["close"], x_label="Date", y_label="VIX close")
    else:
        st.caption("No VIX history available.")
    theme.card_close()
