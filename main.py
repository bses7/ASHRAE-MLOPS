import argparse
import pyarrow
import sys
from src.common.logger import get_logger
from pathlib import Path

from src.common.config_loader import load_yaml_config
from src.ingestion.ingestion import run_ingestion_stage
from src.preprocessing.preprocessor import run_preprocessing_stage
from src.training.trainer import run_training_stage


logger = get_logger("MainPipeline")

def parse_arguments():
    """Parses command line arguments for the MLOps pipeline."""
    parser = argparse.ArgumentParser(
        description="ASHRAE Great Energy Predictor III: Production MLOps Pipeline"
    )
    
    parser.add_argument(
        "--stage", 
        type=str, 
        required=True, 
        choices=["ingestion", "preprocessing", "train", "evaluate", "deploy"],
        help="The specific pipeline stage to execute."
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="configs/pipeline_config.yaml",
        help="Path to the YAML configuration file."
    )

    return parser.parse_args()

def main():
    """Main entry point for all pipeline operations."""
    args = parse_arguments()
    
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {args.config}")
            sys.exit(1)
            
        config = load_yaml_config(str(config_path))
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    try:
        if args.stage == "ingestion":
            logger.info("--- STAGE: DATA INGESTION ---")

            metrics = run_ingestion_stage(config)
            
            if any(m.status == "FAILED" for m in metrics):
                logger.error("Ingestion stage completed with errors.")
                sys.exit(1)
            logger.info("Ingestion stage completed successfully.")

        elif args.stage == "preprocessing":
            logger.info("--- STAGE: DATA PREPROCESSING ---")
            run_preprocessing_stage(config)
            logger.info("Preprocessing stage completed successfully.")

        elif args.stage == "train":
            logger.info("Starting Model Training...")
            metrics = run_training_stage(config)
            logger.warning("Training stage logic not yet implemented.")

        # Add other stages as the pipeline grows...

    except KeyError as e:
        logger.error(f"Configuration error: Missing key {e} in {args.config}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Pipeline failed at stage [{args.stage}]: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()