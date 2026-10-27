"""
Fund Metrics Engine (portfolio/fund_metrics.py)

Computes deterministic risk/return metrics from mutual fund NAV histories:
- CAGR (1Y, 3Y, 5Y, 10Y)
- Rolling 3Y and 5Y returns
- Annualized Volatility
- Maximum Drawdown (MDD)
- Sharpe Ratio (with configurable risk-free rate)
- Tracking Error (for index funds)
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
CACHE_DIR = os.path.join(DATA_DIR, "nav_cache")
RISK_FREE_RATE = 0.065  # 6.5% standard Indian 91-day T-Bill / Repo benchmark


def load_nav_history(scheme_code: int) -> pd.DataFrame:
    """
    Load NAV time series for a scheme from cached JSON.
    Returns DataFrame indexed by date with 'nav' column sorted ascending by date.
    """
    cache_path = os.path.join(CACHE_DIR, f"{scheme_code}.json")
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"NAV cache for scheme {scheme_code} not found at {cache_path}")
    
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    records = data.get("data", [])
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna().sort_values("date").reset_index(drop=True)
    df.set_index("date", inplace=True)
    return df


def compute_cagr(start_nav: float, end_nav: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate."""
    if years <= 0 or start_nav <= 0 or end_nav <= 0:
        return 0.0
    val = (end_nav / start_nav) ** (1.0 / years) - 1.0
    if np.isnan(val) or np.isinf(val):
        return 0.0
    return round(float(val), 4)


def compute_max_drawdown(nav_series: pd.Series) -> float:
    """
    Compute Maximum Drawdown (peak-to-trough decline).
    Returns negative decimal (e.g. -0.25 for -25%).
    """
    if len(nav_series) < 2:
        return 0.0
    peak = nav_series.cummax()
    drawdown = (nav_series - peak) / peak
    val = float(drawdown.min())
    if np.isnan(val) or np.isinf(val):
        return 0.0
    return round(val, 4)


def compute_volatility(nav_series: pd.Series, periods_per_year: int = 252) -> float:
    """Compute annualized volatility from daily log/simple returns."""
    if len(nav_series) < 2:
        return 0.0
    daily_returns = nav_series.pct_change().dropna()
    vol = daily_returns.std() * np.sqrt(periods_per_year)
    if np.isnan(vol) or np.isinf(vol):
        return 0.0
    return round(float(vol), 4)


def compute_sharpe_ratio(cagr: float, volatility: float, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """Compute Sharpe Ratio = (CAGR - Rf) / Volatility."""
    if np.isnan(volatility) or np.isnan(cagr) or volatility <= 0.0001:
        return 0.0
    val = (cagr - risk_free_rate) / volatility
    if np.isnan(val) or np.isinf(val):
        return 0.0
    return round(float(val), 2)


def compute_rolling_returns(nav_series: pd.Series, rolling_years: int = 3) -> Dict[str, float]:
    """
    Compute rolling CAGR summary over given years.
    Returns mean, min, max, and percentage of periods with positive returns.
    """
    days = int(rolling_years * 252)
    if len(nav_series) <= days:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "pct_positive": 0.0}
    
    rolling_cagr = (nav_series / nav_series.shift(days)) ** (1.0 / rolling_years) - 1.0
    rolling_cagr = rolling_cagr.replace([np.inf, -np.inf], np.nan).dropna()
    
    if len(rolling_cagr) == 0:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "pct_positive": 0.0}
    
    mean_val = float(rolling_cagr.mean())
    min_val = float(rolling_cagr.min())
    max_val = float(rolling_cagr.max())
    
    return {
        "mean": round(0.0 if np.isnan(mean_val) or np.isinf(mean_val) else mean_val, 4),
        "min": round(0.0 if np.isnan(min_val) or np.isinf(min_val) else min_val, 4),
        "max": round(0.0 if np.isnan(max_val) or np.isinf(max_val) else max_val, 4),
        "pct_positive": round(float((rolling_cagr > 0).mean()) * 100, 1),
    }


def compute_tracking_error(nav_series: pd.Series, benchmark_series: pd.Series) -> float:
    """
    Compute annualized Tracking Error between fund and benchmark returns.
    """
    merged = pd.concat([nav_series, benchmark_series], axis=1, join="inner").dropna()
    if len(merged) < 30:
        return 0.0
    r_fund = merged.iloc[:, 0].pct_change().dropna()
    r_bench = merged.iloc[:, 1].pct_change().dropna()
    diff = r_fund - r_bench
    te = diff.std() * np.sqrt(252)
    return round(float(te), 4)


def compute_comprehensive_fund_metrics(scheme_code: int, name: str = "", category: str = "") -> Dict[str, Any]:
    """
    Compute full metrics report for a fund from historical NAV.
    """
    df = load_nav_history(scheme_code)
    if df.empty:
        return {"scheme_code": scheme_code, "name": name, "error": "No data"}
        
    nav_s = df["nav"]
    latest_date = df.index[-1]
    latest_nav = float(nav_s.iloc[-1])
    earliest_date = df.index[0]
    total_years = (latest_date - earliest_date).days / 365.25
    
    # 1Y, 3Y, 5Y, 10Y CAGRs
    cagr_metrics = {}
    for y in [1, 3, 5, 10]:
        target_date = latest_date - timedelta(days=int(y * 365.25))
        past_nav = nav_s[nav_s.index <= target_date]
        if not past_nav.empty:
            cagr_metrics[f"cagr_{y}y"] = compute_cagr(past_nav.iloc[-1], latest_nav, y)
        else:
            cagr_metrics[f"cagr_{y}y"] = None

    # Volatility and Drawdown (5-year or all available)
    five_yr_cutoff = latest_date - timedelta(days=int(5 * 365.25))
    s_5y = nav_s[nav_s.index >= five_yr_cutoff]
    if len(s_5y) < 100:
        s_5y = nav_s

    vol_5y = compute_volatility(s_5y)
    mdd_5y = compute_max_drawdown(s_5y)
    cagr_3y = cagr_metrics.get("cagr_3y") or 0.12
    sharpe = compute_sharpe_ratio(cagr_3y, vol_5y)
    
    # Rolling returns
    rolling_3y = compute_rolling_returns(nav_s, rolling_years=3)
    rolling_5y = compute_rolling_returns(nav_s, rolling_years=5)

    return {
        "scheme_code": scheme_code,
        "name": name,
        "category": category,
        "latest_nav": round(latest_nav, 2),
        "as_of_date": latest_date.strftime("%Y-%m-%d"),
        "history_years": round(total_years, 1),
        "cagr_1y": cagr_metrics.get("cagr_1y"),
        "cagr_3y": cagr_metrics.get("cagr_3y"),
        "cagr_5y": cagr_metrics.get("cagr_5y"),
        "cagr_10y": cagr_metrics.get("cagr_10y"),
        "volatility_5y": vol_5y,
        "max_drawdown_5y": mdd_5y,
        "sharpe_ratio": sharpe,
        "rolling_3y": rolling_3y,
        "rolling_5y": rolling_5y,
    }
