# OptionStrat (Streamlit)

A phone-friendly browser app that combines ticker analysis, daily option picks,
SPX/SPY short-dated plays, weekend theta setups, event risk, and VIX analysis.

The dark, card-based look is ported from a companion React app's design
tokens (colors, radius, typography) so both clients share one visual
language — see `optionstrat/theme.py` for the palette and component
builders.

## Setup

```bash
pip install -r requirements.txt
```

## Configuration

The app talks to a separate OptionStrat API. Point it there with an
environment variable:

```bash
export OPTIONSTRAT_API_URL=https://your-api.example.com/api
```

Or, for Streamlit Community Cloud / local secrets, create
`.streamlit/secrets.toml` (do not commit this file):

```toml
OPTIONSTRAT_API_URL = "https://your-api.example.com/api"
```

An `.env.example` is included as a template.

## Run locally

```bash
streamlit run app.py
```

## Tests

```bash
pip install pytest
pytest -q
```

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the main file path to `app.py`.
4. Add `OPTIONSTRAT_API_URL` under **Advanced settings → Secrets**.
5. Deploy. The API must be publicly reachable and allow CORS.

API responses are cached for 60 seconds; use the "Refresh market data"
button in the sidebar to force a re-fetch.
