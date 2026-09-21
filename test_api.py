from pydantic import ValidationError

from optionstrat.models import Analysis, MarketItem, PickCollection, VixPredictor


def test_market_item_preserves_price_with_long_company_name():
    item = MarketItem.model_validate(
        {
            "ticker": "LONG",
            "companyName": "A Very Long Company Name That Must Never Hide Its Price",
            "spotPrice": 123.45,
            "strategy": "Bull Put Spread",
        }
    )
    assert item.spotPrice == 123.45
    assert len(item.companyName or "") > 24


def test_collection_parses_representative_picks():
    result = PickCollection.model_validate(
        {
            "picks": [
                {
                    "ticker": "SPY",
                    "companyName": "SPDR S&P 500 ETF Trust",
                    "spotPrice": 600.0,
                    "strategy": "Iron Condor",
                    "probabilityOfProfit": 0.8,
                }
            ],
            "riskWarning": "Short-dated options carry significant risk.",
        }
    )
    assert result.picks[0].probabilityOfProfit == 0.8


def test_analysis_requires_core_market_fields():
    try:
        Analysis.model_validate({"ticker": "AAPL", "spotPrice": 200})
    except ValidationError:
        pass
    else:
        raise AssertionError("Incomplete analysis unexpectedly validated")


def test_vix_response_parses_chart_data():
    model = VixPredictor.model_validate(
        {
            "vixLevel": 18,
            "vixChange": -0.5,
            "vixChangePct": -2.7,
            "vixPercentile": 45,
            "fearLabel": "Normal",
            "fearColor": "#00aa00",
            "spyPrice": 600,
            "spyChange": 2,
            "spyChangePct": 0.3,
            "expectedMoves": [],
            "vixHistory": [{"date": "2026-09-11", "close": 18}],
            "commentary": "Volatility is near its recent median.",
        }
    )
    assert model.vixHistory[0]["close"] == 18