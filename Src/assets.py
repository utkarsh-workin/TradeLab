from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


ASSETS = {
    # ⭐ Stocks
    "RELIANCE": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "RELIANCE_NS_clean.csv",
    },

    "GACM Technologies": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "GATECH_NS_clean.csv",
    },

    "Eternal": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "ETERNAL_NS_clean.csv",
    },

    "IRFC": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "IRFC_NS_clean.csv",
    },

    "RVNL": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "RVNL_NS_clean.csv",
    },

    "RailTel": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "RAILTEL_NS_clean.csv",
    },

    "Torrent Power": {
        "type": "stock",
        "file": PROJECT_ROOT / "Dataset" / "processed" / "TORRENTPOWER_NS_clean.csv",
    },

    # 📈 Indices
    "NIFTY 50": {
        "type": "index",
        "ticker": "^NSEI",
    },

    "BANK NIFTY": {
        "type": "index",
        "ticker": "^NSEBANK",
    },

    "SENSEX": {
        "type": "index",
        "ticker": "^BSESN",
    },
}