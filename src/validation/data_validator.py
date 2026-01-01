import pandas as pd
import numpy as np
import great_expectations as gx
from pathlib import Path
import datetime
from src.common.logger import get_logger
from great_expectations.data_context.types.base import (
    DataContextConfig,
    FilesystemStoreBackendDefaults,
)

class DataValidator:
    """
    Great Expectations-based Data Validation for Energy, Building, and Weather datasets.
    """

    def __init__(self):
        self.logger = get_logger("DataValidator")

        PROJECT_ROOT = Path(__file__).resolve().parents[2]

        GX_ROOT = PROJECT_ROOT / "src" / "validation" / "gx"
        VALIDATION_DOCS = PROJECT_ROOT / "src" / "validation" / "great_expectations"

        GX_ROOT.mkdir(parents=True, exist_ok=True)
        VALIDATION_DOCS.mkdir(parents=True, exist_ok=True)

        context_config = DataContextConfig(
            store_backend_defaults=FilesystemStoreBackendDefaults(
                root_directory=str(GX_ROOT) 
            ),
            data_docs_sites={
                "local_validation_site": {
                    "class_name": "SiteBuilder",
                    "store_backend": {
                        "class_name": "TupleFilesystemStoreBackend",
                        "base_directory": str(VALIDATION_DOCS), 
                    },
                    "site_index_builder": {
                        "class_name": "DefaultSiteIndexBuilder",
                    },
                }
            },
        )

        self.context = gx.get_context(project_config=context_config)

        self.datasource_name = "ashrae_production_datasource"
        self.datasource = self.context.data_sources.add_or_update_pandas(
            name=self.datasource_name
        )

        self.logger.info(
            f"Great Expectations Data Docs will be written to: {VALIDATION_DOCS}/index.html"
        )

    def validate_ingested_data(self, df_energy: pd.DataFrame, df_building: pd.DataFrame, df_weather: pd.DataFrame) -> bool:
        """Validates Energy, Building, and Weather dataframes."""
        self.logger.info("Starting Data Validation Stage...")
        
        results = [
            self._run_validation(df_energy, "energy_suite", "energy_asset", self._add_energy_expectations),
            self._run_validation(df_building, "building_suite", "building_asset", self._add_building_expectations),
            self._run_validation(df_weather, "weather_suite", "weather_asset", self._add_weather_expectations)
        ]
        
        self.context.build_data_docs()
        self.logger.info("Visual Data Validation Docs generated inside validation/great_expectations/index.html")

        return all(results)

    def _run_validation(self, df: pd.DataFrame, suite_name: str, asset_name: str, expectation_func) -> bool:
        """Boilerplate to setup GX infrastructure and run validation for a specific dataframe."""
        
        try:
            asset = self.datasource.get_asset(asset_name)
        except LookupError:
            asset = self.datasource.add_dataframe_asset(name=asset_name)

        batch_def_name = f"batch_def_{asset_name}"
        try:
            batch_definition = asset.get_batch_definition(batch_def_name)
        except LookupError:
            batch_definition = asset.add_batch_definition_whole_dataframe(batch_def_name)

        suite = self.context.suites.add_or_update(gx.ExpectationSuite(name=suite_name))

        batch = batch_definition.get_batch(batch_parameters={"dataframe": df})
        validator = self.context.get_validator(batch=batch, expectation_suite=suite)

        expectation_func(validator)

        self.context.suites.add_or_update(validator.get_expectation_suite())

        validation_result = validator.validate()
        
        self._print_detailed_report(validation_result, suite_name)
        
        return validation_result.success

    def _add_energy_expectations(self, validator):
        """Rules for fact_energy_usage."""
        validator.expect_column_values_to_not_be_null("building_id")
        validator.expect_column_values_to_not_be_null("meter")
        validator.expect_column_values_to_not_be_null("timestamp")
        validator.expect_column_values_to_be_between("meter_reading", min_value=0, max_value=None)

    def _add_building_expectations(self, validator):
        """Rules for dim_building."""
        validator.expect_column_values_to_not_be_null("building_id")
        validator.expect_column_values_to_not_be_null("site_id")
        validator.expect_column_values_to_not_be_null("square_feet")
        validator.expect_column_values_to_be_in_set(
            "primary_use", 
            ["Education", "Office", "Entertainment/public assembly", "Public services", "Lodging/residential", "Other", "Healthcare", "Parking", "Warehouse/storage", "Manufacturing/industrial", "Retail", "Services", "Technology/science", "Food sales and service", "Utility", "Religious worship"]
        )

    def _add_weather_expectations(self, validator):
        """Rules for dim_weather."""
        validator.expect_column_values_to_not_be_null("site_id")
        validator.expect_column_values_to_not_be_null("timestamp")
        validator.expect_column_values_to_not_be_null("air_temperature")
        validator.expect_column_values_to_be_between("air_temperature", min_value=-60, max_value=60)

    def _print_detailed_report(self, result, name):
        """Ported from your notebook for detailed console output."""
        stats = result.statistics
        print("="*80)
        print(f"DETAILED VALIDATION REPORT: {name}")
        print(f"Executed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        status_icon = "PASSED" if result.success else "FAILED"
        print(f"{'OVERALL STATUS':<20}: {status_icon}")
        print(f"{'SUCCESS RATE':<20}: {stats['success_percent']:.2f}%")
        print(f"{'EXPECTATIONS':<20}: {stats['evaluated_expectations']} total | {stats['successful_expectations']} passed | {stats['unsuccessful_expectations']} failed")
        print("-" * 80)
        print(f"{'COLUMN':<15} | {'EXPECTATION':<35} | {'STATUS'}")
        print("-" * 80)
        
        for res in result.results:
            col = res.expectation_config.kwargs.get("column", "Table")
            etype = res.expectation_config.type
            status = "PASS" if res.success else "FAIL"
            print(f"{str(col):<15} | {etype:<35} | {status}")
            
            if not res.success:
                details = res.result
                count = details.get('unexpected_count', 0)
                total = details.get('element_count', 0)
                print(f"FAILURE DETAIL: {count}/{total} values failed")

        print("="*80 + "\n")