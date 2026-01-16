# ASHRAE GREAT ENERGY PREDICTOR (MLOPS PROJECT)

Welcome to the ASHRAE MLOps project! This repository is designed to streamline and automate the machine learning lifecycle, from development to deployment and monitoring.

## Features

- **Data Ingestion**: Automate the data ingestion to the database.
- **Data Preprocessing**: Automate the feature engineering and preprocessing before model training.
- **Model Training**: Automate the training process with reproducible pipelines.
- **Model Deployment**: Seamlessly deploy models to production environments.
- **Monitoring**: Track model performance and ensure reliability.
- **Version Control**: Manage datasets, code, and models with versioning.

## Prerequisites

- Python 3.8+
- Docker
- Airflow (For Orchestration)
- MariaDB/Columnstore
- Redis
- Miniconda
- Git

## Cloning the repo

```bash
  git clone <Repo_URL>
  cd <path_to_mlops_project>
```

## Folder Structure

```bash
mlops/
├── app/                     # Application (API / service)
├── configs/       # Configuration files (YAML,env, etc.)
├── DAGs/                    # Airflow DAGs
├── Notebooks/       # Jupyter notebooks (EDA,experiments)
├── Raw_Data/                # Raw / source datasets
├── reports/                # Evaluation & Monitoring Report
├── logs/                    # Application & pipeline logs
├── saved_models/            # Exported / offline models
├── src/                     # Core source code
│
├── docker-compose.yaml    # Database Docker Compose setup
├── docker-compose-app.yaml  # App-specific Docker services
├── requirements.txt         # Python dependencies
├── setup.sh         # Environment / service setup script
├── main.py             # Entry point (training /inference)
├── LICENSE                  # Project license
├── ReadMe.md                # Project documentation
```

## Dataset Download & Setup (IMPORTANT)

### Dataset Source

https://www.kaggle.com/competitions/ashrae-energy-prediction/data

Steps to Download and Move the Dataset

- Visit the link above.

- Download all the files (train.csv, building_metadata.csv, weather_train.csv, etc.).

- Extract the downloaded ZIP file.

- Move all extracted CSV files into the Raw_Data/ folder.

Final structure should look like this:

```bash
mlops/
│
├── Raw_Data/
│   ├── train.csv
│   ├── test.csv
│   ├── building_metadata.csv
│   ├── weather_train.csv
│   └── weather_test.csv
│
├── dags/
├── notebooks/
├── README.md
└── docker-compose.yml
```

## Installation

1. Clone the repository:

   ```bash
   git clone <Repo_URL>
   cd mlops
   ```

2. Run setup.sh file

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Follow the Prompts:
   Choose to create a new virtual environment (recommended).

4. Post-Installation:
   - The Virtual Environment will be activated.
   - Airflow environment variables will be configured.
   - MLflow Server will start at: http://localhost:5000

## Orchestration Using Airflow

The main pipeline is managed via the ashrae_pipeline_dag.py.

- DAG Location: Ensure the file in DAGs/ is copied to your Airflow home dags/ folder.

- Processing the full 20 million records takes approximately 17 minutes.

- To test quickly, modify configs/pipeline_config.yaml to use a sample:

```bash
training:
  model_save_path: "saved_models/model.pkl"
  sample_size: 500000
  use_sample: True
```

### Available Service Endpoints (After Orchestration)

| Service                | URL                        |
| ---------------------- | -------------------------- |
| MLFlow Server          | http://localhost:5000      |
| MetaBase (BI & Viz)    | http://localhost:3000      |
| FastAPI Backend (Docs) | http://localhost:8000/docs |
| Frontend Application   | http://localhost:3001      |
| MariaDB                | localhost:3306             |
| Redis                  | localhost:6379             |

### Generated Reports

The reports generated from The Great Expectation and EvidentlyAI are available inside:

1. The Great Expectation

```bash
src/
   validation/
```

2. EvidentlyAI

```bash
src/
   monitoring/
      reports/
```

## Manual Usage (Without Airflow)

1. Data Ingestion Stage:

   ```bash
   python main.py --stage ingestion --config ./configs/pipeline_config.yaml
   ```

2. Data Preprocessing Stage:

   ```bash
   python main.py --stage preprocessing --config ./configs/pipeline_config.yaml
   ```

3. Train a model:

   ```bash
   python main.py --stage train --config ./configs/pipeline_config.yaml
   ```

4. Evaluate model:

   ```bash
   python main.py --stage evaluate --config ./configs/pipeline_config.yaml
   ```

5. Deploy the model:

   ```bash
   python main.py --stage deploy --config ./configs/pipeline_config.yaml
   ```

6. After Deployment you can use the app at: localhost:3001

## Accessing the MariaDB Database

After the completion of the orchestration the mariadb container is available at:

localhost:3306

You can access the database using:

```bash
user: student
password: Student@123!
```

And use the database using,

```bash
USE ashrae_db;
```

## Contributing

Contributions are welcome!

1. Fork the project.
2. Create your feature branch.
3. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please reach out to [bishesh.giri8848@gmail.com](mailto:bishesh.giri8848@gmail.com).
