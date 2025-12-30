import pandas as pd
import numpy as np
import great_expectations as gx
import datetime
from src.common.logger import get_logger

class DataValidator:
    """
    Implements Data Quality Gates using Great Expectations.
    Follows the 'Infrastructure-Suite-Validator' pattern.
    """

    def __init__(self):
        self.logger = get_logger("DataValidator")
        self.context = gx.get_context()
        # Define a single datasource for our pandas dataframes
        self.datasource_name = "ashrae_production_datasource"
        self.datasource = self.context.data_sources.add_or_update_pandas(name=self.datasource_name)

    def validate_ingested_data(self, df_energy: pd.DataFrame, df_building: pd.DataFrame, df_weather: pd.DataFrame) -> bool:
        """Validates Energy, Building, and Weather dataframes."""
        self.logger.info("Starting Data Validation Stage...")
        
        results = [
            self._run_validation(df_energy, "energy_suite", "energy_asset", self._add_energy_expectations),
            self._run_validation(df_building, "building_suite", "building_asset", self._add_building_expectations),
            self._run_validation(df_weather, "weather_suite", "weather_asset", self._add_weather_expectations)
        ]
        
        # Build HTML Data Docs (Visual Reports)
        self.context.build_data_docs()
        self.logger.info("Visual Data Docs generated in gx/uncommitted/data_docs/local_site/index.html")

        return all(results)

    def _run_validation(self, df: pd.DataFrame, suite_name: str, asset_name: str, expectation_func) -> bool:
        """Boilerplate to setup GX infrastructure and run validation for a specific dataframe."""
        
        # 1. Setup Asset and Batch Definition
        try:
            asset = self.datasource.get_asset(asset_name)
        except LookupError:
            asset = self.datasource.add_dataframe_asset(name=asset_name)

        batch_def_name = f"batch_def_{asset_name}"
        try:
            batch_definition = asset.get_batch_definition(batch_def_name)
        except LookupError:
            batch_definition = asset.add_batch_definition_whole_dataframe(batch_def_name)

        # 2. Setup Suite (Create if not exists)
        suite = self.context.suites.add_or_update(gx.ExpectationSuite(name=suite_name))

        # 3. Get Batch and Validator
        batch = batch_definition.get_batch(batch_parameters={"dataframe": df})
        validator = self.context.get_validator(batch=batch, expectation_suite=suite)

        # 4. Apply specific rules
        expectation_func(validator)

        # 5. Save the suite back to context
        self.context.suites.add_or_update(validator.get_expectation_suite())

        # 6. Execute Validation
        validation_result = validator.validate()
        
        # 7. Print Detailed Report (From notebook logic)
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
        # Ensure our ingestion imputation worked - air_temp should be 100% complete
        validator.expect_column_values_to_not_be_null("air_temperature")
        validator.expect_column_values_to_be_between("air_temperature", min_value=-60, max_value=60)

    def _print_detailed_report(self, result, name):
        """Ported from your notebook for detailed console output."""
        stats = result.statistics
        print("="*80)
        print(f"📊 DETAILED VALIDATION REPORT: {name}")
        print(f"Executed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        status_icon = "✅ PASSED" if result.success else "❌ FAILED"
        print(f"{'OVERALL STATUS':<20}: {status_icon}")
        print(f"{'SUCCESS RATE':<20}: {stats['success_percent']:.2f}%")
        print(f"{'EXPECTATIONS':<20}: {stats['evaluated_expectations']} total | {stats['successful_expectations']} passed | {stats['unsuccessful_expectations']} failed")
        print("-" * 80)
        print(f"{'COLUMN':<15} | {'EXPECTATION':<35} | {'STATUS'}")
        print("-" * 80)
        
        for res in result.results:
            col = res.expectation_config.kwargs.get("column", "Table")
            etype = res.expectation_config.type
            status = "✅ PASS" if res.success else "❌ FAIL"
            print(f"{str(col):<15} | {etype:<35} | {status}")
            
            if not res.success:
                details = res.result
                count = details.get('unexpected_count', 0)
                total = details.get('element_count', 0)
                print(f"   └─ ⚠️  FAILURE DETAIL: {count}/{total} values failed")

        print("="*80 + "\n")