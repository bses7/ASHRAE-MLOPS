import time
from typing import Dict, Any, List
from src.ingestion.base import IngestionMetrics
from src.ingestion.csv_reader import CSVIngestor
from src.database.connection import DBClient
from src.database.schema_manager import SchemaManager
from src.ingestion.db_writer import StagingWriter
from src.ingestion.transform import DataTransformer
from src.common.logger import get_logger

logger = get_logger("IngestionOrchestrator")

class IngestionStage:
    def __init__(self, config: Dict[str, Any]):
        self.ingestion_cfg = config.get("ingestion", {})
        self.db_client = DBClient(config.get("db", {}))
        self.writer = StagingWriter(self.db_client)
        self.transformer = DataTransformer() 
        self.schema_manager = SchemaManager(self.db_client)

    def run(self) -> List[IngestionMetrics]:
        logger.info("Starting Direct-to-ColumnStore Ingestion Stage...")
        
        self.schema_manager.create_production_tables()
        
        metrics_report = []
        for file_info in self.ingestion_cfg.get("files", []):
            metrics = self._ingest_file(file_info)
            metrics_report.append(metrics)
        
        return metrics_report

    def _ingest_file(self, file_info: Dict) -> IngestionMetrics:
        start_time = time.time()
        name, table = file_info['name'], file_info['table']
        
        self.writer.truncate_table(table)

        reader = CSVIngestor(file_info['path'], name, batch_size=200000)
        total_rows = 0
        for raw_chunk in reader.read_chunks():
            # ETL: Extract -> Transform -> Load
            clean_chunk = self.transformer.transform(raw_chunk, name)
            self.writer.write_chunk(clean_chunk, table)
            total_rows += len(clean_chunk)
            
        return IngestionMetrics(name, total_rows, round(time.time()-start_time, 2), "SUCCESS")
    
    def _summarize(self, reports: List[IngestionMetrics]):
        logger.info("--- INGESTION SUMMARY ---")
        for r in reports:
            logger.info(f"TABLE: {r.entity_name.upper()} | ROWS: {r.rows_processed} | STATUS: {r.status}")

def run_ingestion_stage(config: Dict[str, Any]):
    """Entry point for main.py."""
    stage = IngestionStage(config)
    return stage.run()