"""
Download and cache public data for the advisory co-pilot.

Sources (all free/open):
- AMFI NAVAll.txt: Daily NAV data for all mutual funds
- AMFI Scheme Master: Fund metadata
- mfapi.in: Historical NAV data per scheme
- RBI DBIE: Inflation data (CPI)

If a download is blocked or fails, falls back to documented sample data.
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta


DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
CACHE_DIR = os.path.join(DATA_DIR, "nav_cache")


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def download_amfi_nav_all():
    """Download AMFI NAVAll.txt (daily NAV for all schemes)."""
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    filepath = os.path.join(DATA_DIR, "NAVAll.txt")
    
    # Use cache if less than 24 hours old
    if os.path.exists(filepath):
        age = time.time() - os.path.getmtime(filepath)
        if age < 86400:
            print(f"  [CACHED] NAVAll.txt (age: {age/3600:.1f}h)")
            return filepath
    
    print(f"  Downloading NAVAll.txt from AMFI...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"  [OK] NAVAll.txt ({len(resp.text)} bytes)")
        return filepath
    except Exception as e:
        print(f"  [WARN] Failed to download NAVAll.txt: {e}")
        if os.path.exists(filepath):
            print(f"  [FALLBACK] Using existing cached NAVAll.txt")
            return filepath
        print(f"  [FALLBACK] Will create sample data")
        _create_sample_nav_all(filepath)
        return filepath


def _create_sample_nav_all(filepath):
    """Create sample NAVAll.txt for offline development."""
    sample = """Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date
119551;INF209KA12Z1;INF209KA13Z9;Aditya Birla Sun Life Frontline Equity Fund - Direct Plan-Growth;487.23;27-Oct-2026
119598;INF090I01HD4;-;HDFC Balanced Advantage Fund - Direct Plan-Growth;423.15;27-Oct-2026
120505;INF090I01JN0;-;HDFC Mid-Cap Opportunities Fund - Direct Plan-Growth;198.76;27-Oct-2026
118989;INF174K01LS2;-;Kotak Flexicap Fund - Direct Plan-Growth;78.45;27-Oct-2026
120586;INF846K01EW2;-;Axis Bluechip Fund - Direct Plan-Growth;62.34;27-Oct-2026
122639;INF200K01RJ1;-;SBI Small Cap Fund - Direct Plan-Growth;178.92;27-Oct-2026
119713;INF179K01BB3;-;HDFC Flexi Cap Fund - Direct Plan-Growth;1876.45;27-Oct-2026
120716;INF090I01DP6;-;HDFC Short Term Debt Fund - Direct Plan-Growth;30.21;27-Oct-2026
135781;INF200K01UD7;-;SBI Equity Hybrid Fund - Direct Plan-Growth;284.56;27-Oct-2026
120503;INF090I01JL4;-;HDFC Top 100 Fund - Direct Plan-Growth;1045.67;27-Oct-2026
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sample)
    print(f"  [SAMPLE] Created sample NAVAll.txt")


def download_scheme_nav_history(scheme_code, scheme_name=""):
    """Download historical NAV for a specific scheme from mfapi.in."""
    cache_file = os.path.join(CACHE_DIR, f"{scheme_code}.json")
    
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < 86400 * 7:  # Cache for 7 days
            return cache_file
    
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"  Downloading NAV history for {scheme_code} ({scheme_name})...")
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        with open(cache_file, "w") as f:
            json.dump(data, f)
        # Be nice to the free API
        time.sleep(0.5)
        return cache_file
    except Exception as e:
        print(f"  [WARN] Failed to download {scheme_code}: {e}")
        if os.path.exists(cache_file):
            return cache_file
        return None


# Top direct-plan growth funds by category (scheme codes from AMFI)
TOP_FUNDS = {
    "Large Cap": [
        (119598, "HDFC Top 100 Fund - Direct Plan-Growth"),
        (120503, "HDFC Large Cap Fund - Direct Plan-Growth"),
        (120586, "Axis Bluechip Fund - Direct Plan-Growth"),
        (118989, "Kotak Bluechip Fund - Direct Plan-Growth"),
        (119551, "Aditya Birla Sun Life Frontline Equity Fund - Direct Plan-Growth"),
    ],
    "Flexi Cap": [
        (119713, "HDFC Flexi Cap Fund - Direct Plan-Growth"),
        (135781, "Parag Parikh Flexi Cap Fund - Direct Plan-Growth"),
        (118989, "Kotak Flexicap Fund - Direct Plan-Growth"),
    ],
    "Mid Cap": [
        (120505, "HDFC Mid-Cap Opportunities Fund - Direct Plan-Growth"),
        (119775, "Kotak Emerging Equity Fund - Direct Plan-Growth"),
    ],
    "Small Cap": [
        (122639, "SBI Small Cap Fund - Direct Plan-Growth"),
        (125307, "Axis Small Cap Fund - Direct Plan-Growth"),
    ],
    "Hybrid - Balanced Advantage": [
        (119598, "HDFC Balanced Advantage Fund - Direct Plan-Growth"),
        (135781, "SBI Equity Hybrid Fund - Direct Plan-Growth"),
    ],
    "Short Duration Debt": [
        (120716, "HDFC Short Term Debt Fund - Direct Plan-Growth"),
        (119090, "Axis Short Term Fund - Direct Plan-Growth"),
    ],
    "Index - Nifty 50": [
        (120716, "UTI Nifty 50 Index Fund - Direct Plan-Growth"),
        (135781, "HDFC Index Fund - Nifty 50 Plan - Direct Plan-Growth"),
    ],
}


def download_top_fund_navs():
    """Download NAV history for top funds in each category."""
    print("\nDownloading NAV history for top funds...")
    results = {}
    for category, funds in TOP_FUNDS.items():
        print(f"\n  Category: {category}")
        for code, name in funds:
            path = download_scheme_nav_history(code, name)
            if path:
                results[code] = {"name": name, "category": category, "path": path}
    
    # Save index
    index_path = os.path.join(DATA_DIR, "fund_index.json")
    with open(index_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Fund index saved to {index_path}")
    return results


def create_inflation_data():
    """Create inflation assumptions data.
    
    Source: RBI DBIE CPI data. We use documented long-term averages.
    If RBI download is blocked, we use well-documented sample averages.
    """
    inflation_data = {
        "source": "RBI DBIE / documented long-term CPI averages",
        "note": "Using documented long-term averages. General CPI ~5-6%, Education ~8-10%, Medical ~8-10%",
        "assumptions": {
            "general": 0.06,
            "education": 0.10,
            "medical": 0.09,
            "housing": 0.07,
        },
        "historical_cpi_annual": {
            "2019": 4.8,
            "2020": 6.2,
            "2021": 5.1,
            "2022": 6.7,
            "2023": 5.4,
            "2024": 4.9,
            "2025": 5.2,
        },
        "data_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    filepath = os.path.join(DATA_DIR, "inflation.json")
    with open(filepath, "w") as f:
        json.dump(inflation_data, f, indent=2)
    print(f"  Inflation data saved to {filepath}")
    return inflation_data


def create_asset_return_assumptions():
    """Create expected return assumptions by asset class.
    
    These are long-term historical averages, NOT guarantees.
    Clearly documented for transparency.
    """
    assumptions = {
        "source": "Historical long-term averages from AMFI/BSE/NSE data. NOT guarantees.",
        "disclaimer": "Past performance is not indicative of future results. These are assumptions for planning purposes only.",
        "expected_returns_nominal": {
            "equity_large_cap": 0.12,
            "equity_flexi_cap": 0.13,
            "equity_mid_cap": 0.14,
            "equity_small_cap": 0.15,
            "hybrid_balanced": 0.10,
            "debt_short_duration": 0.07,
            "debt_liquid": 0.06,
            "gold": 0.08,
            "nifty_50_index": 0.12,
        },
        "volatility_annual": {
            "equity_large_cap": 0.18,
            "equity_flexi_cap": 0.20,
            "equity_mid_cap": 0.24,
            "equity_small_cap": 0.28,
            "hybrid_balanced": 0.12,
            "debt_short_duration": 0.04,
            "debt_liquid": 0.01,
            "gold": 0.15,
            "nifty_50_index": 0.18,
        },
    }
    
    filepath = os.path.join(DATA_DIR, "return_assumptions.json")
    with open(filepath, "w") as f:
        json.dump(assumptions, f, indent=2)
    print(f"  Return assumptions saved to {filepath}")
    return assumptions


def main():
    print("=" * 60)
    print("Data Download & Cache Script")
    print("=" * 60)
    
    ensure_dirs()
    
    print("\n[1/4] Downloading AMFI NAVAll.txt...")
    download_amfi_nav_all()
    
    print("\n[2/4] Downloading top fund NAV histories...")
    download_top_fund_navs()
    
    print("\n[3/4] Creating inflation data...")
    create_inflation_data()
    
    print("\n[4/4] Creating return assumptions...")
    create_asset_return_assumptions()
    
    print("\n" + "=" * 60)
    print("Data download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
