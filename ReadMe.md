# ASHRAE GREAT ENERGY PREDICTOR MLOps Project

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

## Installation

1. Clone the repository:

   ```bash
   git clone <Repo_URL>
   cd mlops
   ```

2. Create a virtual environment

   ```bash
   conda create -n <venv_name> python=3.9
   conda activate <venv_name>
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the DB and Analytics Environment (DB will be running in :3306 port and MetaBase Will be running in :3000)

   ```bash
   sudo chmod -R 0755 ./start.sh

    # Uses the docker-compose.yaml available
   ./start.sh
   ```

5. Create a .env file referencing the .env_sample provided inside the mlops directory

## Dataset Download & Setup

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

## Usage

1. Data Ingestion Stage:

   ```bash
   python main.py --stage ingestion --config ./configs/ingestion_config.yaml
   ```

2. Data Preprocessing Stage:

   ```bash
   python main.py --stage preprocessing --config ./configs/ingestion_config.yaml
   ```

3. Train a model:

   ```bash
   python main.py --stage model_training --config ./configs/ingestion_config.yaml
   ```

4. Deploy the model:

   ```bash
   python main.py --stage model_deployment --config ./configs/ingestion_config.yaml
   ```

5. Monitor the model:
   ```bash
   python monitor.py
   ```

## Orchestration Using Airflow

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please reach out to [bishesh.giri8848@gmail.com](mailto:bishesh.giri8848@gmail.com).
