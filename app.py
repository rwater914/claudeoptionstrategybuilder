from __future__ import annotations

import streamlit as st

from optionstrat import theme
from optionstrat.api import OptionStratClient, OptionStratError, _request
from optionstrat.views import render_analysis, render_index, render_market_item, render_vix

st.set_page_config(page_title="OptionStrat", page_icon="📈", layout="centered")
theme.inject_theme()

PAGES = ["Analyze", "Daily picks", "Index plays", "VIX predictor"]
RECENT_TICKERS = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMZN", "MSFT"]

st.session_state.setdefault("nav", "Analyze")


def refresh() -> None:
    _request.clear()
    st.rerun()


def show_error(exc: Exception) -> None:
    st.error(str(exc))
    st.caption("Check the API URL in OPTIONSTRAT_API_URL or Streamlit secrets, then try again.")


def run_analysis(raw_ticker: str, client: OptionStratClient) -> None:
    ticker = raw_ticker.strip().upper()
    if not ticker or not ticker.replace(".", "").replace("-", "").isalnum():
        st.warning("Enter a valid ticker symbol.")
        return
    with st.spinner(f"Analyzing {ticker}…"):
        st.session_state["analysis"] = client.analyze(ticker)
        st.session_state["analysis_ticker"] = ticker


# ---------------------------------------------------------------------------
# Header: dot + title, plus quick links to the two other "hub" pages.
# Mirrors the React app's top bar (Web OptionStrat / SPX·SPY / VIX).
# ---------------------------------------------------------------------------

head_left, head_mid, head_right = st.columns([5, 2.2, 1.8])
with head_left:
    theme.header("OptionStrat")
with head_mid:
    if st.button("SPX · SPY", key="nav_index_pill", type="secondary", use_container_width=True):
        st.session_state["nav"] = "Index plays"
        st.rerun()
with head_right:
    if st.button("VIX", key="nav_vix_pill", type="secondary", use_container_width=True):
        st.session_state["nav"] = "VIX predictor"
        st.rerun()

st.caption("Options research in your browser. No Expo Go required.")

with st.sidebar:
    page = st.radio("Navigate", PAGES, key="nav")
    if st.button("Refresh market data", use_container_width=True):
        refresh()
    st.divider()
    st.caption("Educational analysis only — not financial advice.")

client = OptionStratClient()

try:
    if page == "Analyze":
        st.header("Analyze a ticker")
        with st.form("ticker_form"):
            ticker_input = st.text_input("Ticker", placeholder="AAPL", max_chars=10)
            submitted = st.form_submit_button("Analyze →", type="primary", use_container_width=True)

        st.markdown('<div class="os-chip-row"></div>', unsafe_allow_html=True)
        chip_cols = st.columns(len(RECENT_TICKERS))
        clicked_chip: str | None = None
        for col, t in zip(chip_cols, RECENT_TICKERS):
            with col:
                is_active = st.session_state.get("analysis_ticker") == t
                if st.button(
                    t,
                    key=f"chip_{t}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    clicked_chip = t

        if submitted:
            run_analysis(ticker_input, client)
        if clicked_chip:
            run_analysis(clicked_chip, client)

        if "analysis" in st.session_state:
            render_analysis(st.session_state["analysis"])
        else:
            theme.empty_state(
                "Pick a ticker to begin",
                "Get suggested bull put spreads at 20, 13 and 11 deltas across 7, 14, 21, "
                "30 and 41 days. Plus expected price ranges and a market rationale.",
                icon_name="activity",
            )

    elif page == "Daily picks":
        st.header("Daily option ideas")
        labels = {
            "Bull put spread": ("pick", None),
            "Iron condor": ("condor-pick", None),
            "$100 account": ("small-pick", {"budget": 100}),
            "$200 account": ("small-pick", {"budget": 200}),
            "Short term": ("short-term-picks", None),
            "Tasty mechanics": ("tasty-picks", None),
            "Weekend theta": ("weekend-pick", None),
        }
        selection = st.selectbox("Pick type", list(labels))
        path, params = labels[selection]
        with st.spinner("Loading current pick…"):
            if selection in {"Short term", "Tasty mechanics"}:
                collection = client.picks(path)
                if not collection.picks:
                    theme.empty_state("No picks right now", "Check back after the next market data refresh.")
                for item in collection.picks:
                    render_market_item(item)
                note = collection.managementNote or collection.riskWarning
                if note:
                    st.warning(note)
            else:
                render_market_item(client.pick(path, params), badge_label=selection)

    elif page == "Index plays":
        st.header("SPX / SPY index plays")
        index = st.segmented_control("Underlying", ["SPX", "SPY"], default="SPX")
        with st.spinner(f"Building {index} probability tiers…"):
            render_index(client.index_picks(index or "SPX"))

    else:
        st.header("VIX predictor")
        with st.spinner("Loading volatility data…"):
            render_vix(client.vix())

except OptionStratError as exc:
    show_error(exc)
