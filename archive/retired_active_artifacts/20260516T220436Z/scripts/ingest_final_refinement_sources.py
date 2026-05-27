#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PROXY_DIR = ROOT / "data" / "raw" / "eu_de" / "monthly_proxy_candidates"
BANKING_DIR = ROOT / "data" / "raw" / "eu_de" / "banking_proxy_candidates"


@dataclass(frozen=True)
class Source:
    file_name: str
    url: str
    source_family: str
    source_name: str
    frequency: str
    transformation_note: str
    parser: str = "raw_csv"


SOURCES: tuple[Source, ...] = (
    Source(
        "ecb_wage_tracker_coverage.csv",
        "https://data-api.ecb.europa.eu/service/data/EWT/M.U2.N.WT.COVR._T.4F0._Z?format=csvdata",
        "compensation",
        "ECB Wage Tracker coverage",
        "monthly",
        "Observed monthly EWT coverage diagnostic; not a compensation response proxy.",
    ),
    Source(
        "eurostat_unemployment_ea21_sa.csv",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m?geo=EA21&sex=T&age=TOTAL&s_adj=SA&unit=PC_ACT",
        "labor_tightness",
        "Eurostat monthly unemployment rate",
        "monthly",
        "Seasonally adjusted unemployment rate; inverted in processed data so higher values mean tighter labor markets.",
        "eurostat_json",
    ),
    Source(
        "eurostat_ecfin_employment_expectations_ea20.csv",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ei_bsee_m_r2?geo=EA20&indic=BS-EEI-I&s_adj=SA&unit=INX",
        "labor_tightness",
        "European Commission employment expectations indicator",
        "monthly",
        "Monthly aggregate employment expectations indicator; indirect wage-pressure proxy.",
        "eurostat_json",
    ),
    Source(
        "eurostat_ecfin_services_employment_expectations_ea20.csv",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ei_bsee_m_r2?geo=EA20&indic=BS-SEEM-BAL&s_adj=SA&unit=BAL",
        "labor_tightness",
        "European Commission services employment expectations",
        "monthly",
        "Monthly services-sector employment expectations balance; indirect services wage-pressure proxy.",
        "eurostat_json",
    ),
    Source(
        "ecb_ces_income_expectations_12m_median.csv",
        "https://data-api.ecb.europa.eu/service/data/CES/M.Z18.ALL.T.C3220.NUM_VAR.WM?format=csvdata",
        "household_income_pressure",
        "ECB Consumer Expectations Survey household income expectations",
        "monthly",
        "Weighted median household net-income expectations over the next 12 months; short public CES sample.",
    ),
    Source(
        "ecb_ces_unemployment_expectations_12m_median.csv",
        "https://data-api.ecb.europa.eu/service/data/CES/M.Z18.ALL.T.C4031.NUM_VAR.WM?format=csvdata",
        "labor_tightness",
        "ECB Consumer Expectations Survey unemployment expectations",
        "monthly",
        "Weighted median expected unemployment rate over the next 12 months; short public CES sample.",
    ),
    Source(
        "eurostat_sts_industry_wage_bill_de.csv",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inlb_m?geo=DE&indic_bt=WAGE&nace_r2=B-E36&s_adj=NSA&unit=I21",
        "compensation",
        "Eurostat STS industry gross wages and salaries index",
        "monthly",
        "Monthly German industry wage-bill index; processed as real year-on-year wage-bill pressure.",
        "eurostat_json",
    ),
    Source(
        "ecb_bls_credit_standards_mortgage.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.Z.H.H.B3.ST.S.WFNET?format=csvdata",
        "banking",
        "ECB BLS mortgage credit standards",
        "quarterly",
        "Quarterly BLS net tightening for loans to households for house purchase; quarter-end observed only.",
    ),
    Source(
        "ecb_bls_credit_standards_nfc.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.O.E.Z.B3.ST.S.WFNET?format=csvdata",
        "banking",
        "ECB BLS enterprise credit standards",
        "quarterly",
        "Quarterly BLS net tightening for enterprise loans; quarter-end observed only.",
    ),
    Source(
        "ecb_bls_credit_standards_consumer.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.Z.H.C.B3.ST.S.WFNET?format=csvdata",
        "banking",
        "ECB BLS consumer-credit standards",
        "quarterly",
        "Quarterly BLS net tightening for consumer credit; quarter-end observed only.",
    ),
    Source(
        "ecb_bls_loan_demand_mortgage.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.Z.H.H.B3.ZZ.D.WFNET?format=csvdata",
        "banking",
        "ECB BLS mortgage loan demand",
        "quarterly",
        "Quarterly BLS net demand for loans to households for house purchase; quarter-end observed only.",
    ),
    Source(
        "ecb_bls_loan_demand_nfc.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.O.E.Z.B3.ZZ.D.WFNET?format=csvdata",
        "banking",
        "ECB BLS enterprise loan demand",
        "quarterly",
        "Quarterly BLS net demand for enterprise loans; quarter-end observed only.",
    ),
    Source(
        "ecb_bls_loan_demand_consumer.csv",
        "https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.Z.H.C.B3.ZZ.D.WFNET?format=csvdata",
        "banking",
        "ECB BLS consumer-credit demand",
        "quarterly",
        "Quarterly BLS net demand for consumer credit; quarter-end observed only.",
    ),
    Source(
        "ecb_mir_mortgage_lending_rate.csv",
        "https://data-api.ecb.europa.eu/service/data/MIR/M.U2.B.A2C.A.R.A.2250.EUR.N?format=csvdata",
        "banking",
        "ECB MIR mortgage lending rate",
        "monthly",
        "Monthly annualised agreed rate on new house-purchase loans; lending spread is computed against monthly average DFR.",
    ),
    Source(
        "ecb_mir_nfc_lending_rate.csv",
        "https://data-api.ecb.europa.eu/service/data/MIR/M.U2.B.A2A.A.R.A.2240.EUR.N?format=csvdata",
        "banking",
        "ECB MIR NFC lending rate",
        "monthly",
        "Monthly annualised agreed rate on new NFC loans; lending spread is computed against monthly average DFR.",
    ),
)


def target_dir(source: Source) -> Path:
    return BANKING_DIR if source.source_family == "banking" else PROXY_DIR


def fetch(url: str, attempts: int = 3) -> bytes:
    request = Request(url, headers={"User-Agent": "THESIS_Model empirical refinement"})
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == attempts:
                raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}")


def dimension_codes(dataset: dict, dimension: str) -> list[str]:
    index = dataset["dimension"][dimension]["category"]["index"]
    return [code for code, _ in sorted(index.items(), key=lambda item: item[1])]


def flat_index_to_coords(index: int, sizes: list[int]) -> list[int]:
    coords = [0] * len(sizes)
    for pos in range(len(sizes) - 1, -1, -1):
        size = sizes[pos]
        coords[pos] = index % size
        index //= size
    return coords


def eurostat_json_to_csv(payload: bytes, source: Source) -> str:
    dataset = json.loads(payload.decode("utf-8"))
    ids: list[str] = dataset["id"]
    sizes: list[int] = dataset["size"]
    code_lists = {dimension: dimension_codes(dataset, dimension) for dimension in ids}
    rows: list[dict[str, object]] = []
    labels = dataset.get("dimension", {})
    for flat_key, value in dataset.get("value", {}).items():
        coords = flat_index_to_coords(int(flat_key), sizes)
        row = {dimension.upper(): code_lists[dimension][coords[i]] for i, dimension in enumerate(ids)}
        row["TIME_PERIOD"] = row.pop("TIME")
        row["OBS_VALUE"] = value
        row["TITLE"] = dataset.get("label", source.source_name)
        row["SOURCE_URL"] = source.url
        for dimension, code in list(row.items()):
            if dimension in {"TIME_PERIOD", "OBS_VALUE", "TITLE", "SOURCE_URL"}:
                continue
            label_map = labels.get(dimension.lower(), {}).get("category", {}).get("label", {})
            row[f"{dimension}_LABEL"] = label_map.get(str(code), "")
        rows.append(row)
    if not rows:
        rows.append(
            {
                "TIME_PERIOD": "",
                "OBS_VALUE": "",
                "TITLE": dataset.get("label", source.source_name),
                "SOURCE_URL": source.url,
                "NOTE": "No observations returned for this exact official query.",
            }
        )
    fieldnames = sorted({key for row in rows for key in row})
    ordered = ["TIME_PERIOD", "OBS_VALUE", *[field for field in fieldnames if field not in {"TIME_PERIOD", "OBS_VALUE"}]]
    output: list[str] = []
    writer = csv.DictWriter(_ListWriter(output), fieldnames=ordered, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "".join(output)


class _ListWriter:
    def __init__(self, output: list[str]) -> None:
        self.output = output

    def write(self, text: str) -> int:
        self.output.append(text)
        return len(text)


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    PROXY_DIR.mkdir(parents=True, exist_ok=True)
    BANKING_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, object]] = []
    for source in SOURCES:
        payload = fetch(source.url)
        out_dir = target_dir(source)
        path = out_dir / source.file_name
        if source.parser == "eurostat_json":
            path.write_text(eurostat_json_to_csv(payload, source), encoding="utf-8")
        else:
            path.write_bytes(payload)
        manifest_rows.append(
            {
                "file_name": source.file_name,
                "path": str(path.relative_to(ROOT)),
                "source_family": source.source_family,
                "source_name": source.source_name,
                "frequency": source.frequency,
                "source_url": source.url,
                "transformation_note": source.transformation_note,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "raw_overwrite_policy": "refreshable official API pull; source URL retained for reproducibility",
            }
        )
        print(f"Wrote {path.relative_to(ROOT)}")
    for out_dir in (PROXY_DIR, BANKING_DIR):
        rows = [row for row in manifest_rows if Path(str(row["path"])).parent == out_dir.relative_to(ROOT)]
        manifest_path = out_dir / "source_manifest_refinement.csv"
        with manifest_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
