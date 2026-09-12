"""Regression checks for the demonstration CSV used by the Streamlit dashboard."""

import csv
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "geosentinel_monthly_dashboard_data.csv"

REQUIRED_COLUMNS = [
    "data_center_name",
    "latitude",
    "longitude",
    "year_month",
    "mean_LST_C",
    "mean_NDWI",
    "mean_NDVI",
    "mean_NDBI",
    "precipitation_mm",
    "soil_moisture",
    "lst_change_1y",
    "ndwi_change_1y",
    "ndvi_change_1y",
    "ndbi_change_1y",
    "ECI_score",
    "ESS_score",
    "risk_score",
    "risk_level",
    "forecast_risk_score_6m",
    "forecast_risk_level_6m",
    "forecast_risk_score_12m",
    "forecast_risk_level_12m",
]


class DashboardDataSchemaTests(unittest.TestCase):
    def test_csv_has_the_required_dashboard_columns(self):
        with DATA_FILE.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.assertEqual(reader.fieldnames, REQUIRED_COLUMNS)

    def test_csv_has_rows_and_anonymised_location_labels(self):
        with DATA_FILE.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        self.assertGreater(len(rows), 0)
        self.assertTrue(all(row["data_center_name"].startswith("US_Region_") for row in rows))

    def test_required_values_are_present_in_each_row(self):
        with DATA_FILE.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        for row_number, row in enumerate(rows, start=2):
            for column in REQUIRED_COLUMNS:
                self.assertNotEqual(row[column], "", f"Missing {column} at CSV row {row_number}")


if __name__ == "__main__":
    unittest.main()
