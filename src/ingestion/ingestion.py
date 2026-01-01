import time
from typing import Dict, Any, List
from src.ingestion.base import IngestionMetrics
from src.ingestion.csv_reader import CSVIngestor
from src.database.connection import DBClient
from src.ingestion.db_writer import StagingWriter
from src.ingestion.transform import DataTransformer
from src.database.schema_manager import SchemaManager # Added
from src.common.logger import get_logger

logger = get_logger("IngestionOrchestrator")

class IngestionStage:
    def __init__(self, config: Dict[str, Any]):
        self.ingestion_cfg = config.get("ingestion", {})
        self.db_client = DBClient(config.get("db", {}))
        self.writer = StagingWriter(self.db_client)
        self.transformer = DataTransformer()
        self.schema_manager = SchemaManager(self.db_client) # Initialize

    def run(self) -> List[IngestionMetrics]:
        logger.info("Starting Ingestion Stage...")
        
        self.schema_manager.create_production_tables()
        
        metrics_report = []
        for file_info in self.ingestion_cfg.get("files", []):
            if file_info['table'] == "fact_energy_usage":
                metrics = self._bulk_ingest_fact(file_info)
            else:
                metrics = self._chunked_ingest_dim(file_info)
            metrics_report.append(metrics)
        
        self._summarize(metrics_report)
        return metrics_report

    def _bulk_ingest_fact(self, file_info: Dict) -> IngestionMetrics:
        """ColumnStore Bulk Loader."""
        start_time = time.time()
        table = file_info['table']
        
        logger.info(f"Direct Bulk Loading {file_info['name']} -> {table}")
        
        self.writer.truncate_table(table)
        
        columns = ["building_id", "meter", "timestamp", "meter_reading"]
        
        self.writer.bulk_load_csv(file_info['path'], table, columns)
        
        return IngestionMetrics(file_info['name'], -1, round(time.time()-start_time, 2), "BULK_SUCCESS")

    def _chunked_ingest_dim(self, file_info: Dict) -> IngestionMetrics:
        """Dimension Tables."""
        start_time = time.time()
        name, path, table = file_info['name'], file_info['path'], file_info['table']
        total_rows = 0
        
        logger.info(f"Chunked ETL process for {name} -> {table}")
        reader = CSVIngestor(path, name)
        
        self.writer.truncate_table(table)
        
        for raw_chunk in reader.read_chunks():
            clean_chunk = self.transformer.transform(raw_chunk, name)
            self.writer.write_chunk(clean_chunk, table)
            total_rows += len(clean_chunk)
            
        return IngestionMetrics(name, total_rows, round(time.time()-start_time, 2), "SUCCESS")
    
    def _summarize(self, reports: List[IngestionMetrics]):
        logger.info("--- INGESTION SUMMARY ---")
        for r in reports:
            rows = "N/A (Bulk)" if r.rows_processed == -1 else r.rows_processed
            logger.info(f"TABLE: {r.entity_name.upper()} | ROWS: {rows} | TIME: {r.execution_time_seconds}s")

def run_ingestion_stage(config: Dict[str, Any]):
    stage = IngestionStage(config)
    return stage.run()