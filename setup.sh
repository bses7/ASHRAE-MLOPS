#!/bin/bash

set -e

# -------------------------------
# 1. Conda Environment Setup
# -------------------------------
echo "--- Conda Environment Setup ---"

if ! command -v conda &> /dev/null; then
    echo "ERROR: conda could not be found. Please install Miniconda/Anaconda first."
    exit 1
fi

echo "Do you want to create a new Conda environment or use an existing one?"
echo "1) Create a new environment"
echo "2) Use an existing environment"
echo "Recommended: Create a new environment to avoid dependency conflicts."

read -p "Selection (1 or 2): " ENV_CHOICE

read -p "Enter the name of the virtual environment: " VENV_NAME

CONDA_BASE=$(conda info --base)
VENV_PATH="${CONDA_BASE}/envs/${VENV_NAME}/bin/python"

case $ENV_CHOICE in
    1)
        if conda info --envs | grep -q -w "$VENV_NAME"; then
            echo "Error: Environment '$VENV_NAME' already exists. Cannot create a new one with that name."
            exit 1
        fi
        
        echo "Creating new environment '$VENV_NAME'..."
        conda create -y -n "$VENV_NAME" python=3.11.13
        
        if [ -f "requirements.txt" ]; then
            echo "Installing requirements from requirements.txt..."
            conda run -n "$VENV_NAME" pip install -r requirements.txt
        else
            echo "Warning: requirements.txt not found. Please install libraries manually."
        fi
        ;;
    
    2)
        if ! conda info --envs | grep -q -w "$VENV_NAME"; then
            echo "ERROR: Environment '$VENV_NAME' does not exist."
            echo "Available environments:"
            conda env list
            exit 1
        fi
        echo "Using existing environment: $VENV_NAME"
        echo "Please ensure you have all required libraries listed in ReadMe (pandas, sqlalchemy, etc.) installed in your '$VENV_NAME'."
        sleep 2
        ;;
    
    *)
        echo "Invalid selection. Exiting."
        exit 1
        ;;
esac

echo "Using VENV_PATH: $VENV_PATH"
echo "--------------------------------"

# -------------------------------
# 2. Docker Setup
# -------------------------------

echo "---------------------------------------------"
echo "Starting DATABASE AND METABASE containers..."
echo "---------------------------------------------"

docker-compose up -d

echo "Waiting for MariaDB to be ready..."
until docker exec mcs_container mariadb -e "SELECT 1;" >/dev/null 2>&1; do
  sleep 2
done

echo "MariaDB is up"

echo "Provisioning ColumnStore..."
docker exec -it mcs_container provision 

docker exec -i mcs_container mariadb <<EOF
GRANT ALL PRIVILEGES ON *.* TO 'student'@'%' IDENTIFIED BY 'Student@123!';
GRANT ALL PRIVILEGES ON *.* TO 'student'@'localhost' IDENTIFIED BY 'Student@123!';
FLUSH PRIVILEGES;
CREATE OR REPLACE DATABASE ashrae_db;
EOF

echo "MariaDB setup completed"

# -------------------------------
# 3. Airflow Setup
# -------------------------------

echo "--------------------------------"
echo "Configuring Airflow..."
echo "--------------------------------"

if [ -z "$AIRFLOW_HOME" ]; then
  echo "AIRFLOW_HOME not set, defaulting to $HOME/airflow"
  export AIRFLOW_HOME="$HOME/airflow"
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AIRFLOW_DAGS_DIR="$AIRFLOW_HOME/dags"
DAG_SOURCE="$PROJECT_ROOT/DAGs/ashrae_pipeline_dag.py"

# mkdir -p "$AIRFLOW_DAGS_DIR"

if [ ! -f "$DAG_SOURCE" ]; then
  echo "ERROR: DAG file not found at $DAG_SOURCE"
  exit 1
fi

echo "Deploying Airflow DAG..."
cp "$DAG_SOURCE" "$AIRFLOW_DAGS_DIR/"

# -------------------------------
# 4. Set Airflow Variables
# -------------------------------
echo "Setting Airflow Variables..."

export AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR

airflow variables set PROJECT_HOME "$PROJECT_ROOT"
airflow variables set VENV "$VENV_NAME"
airflow variables set CONFIG_PATH "$PROJECT_ROOT/configs/pipeline_config.yaml"
airflow variables set VENV_PATH "$VENV_PATH"

unset AIRFLOW__LOGGING__LOGGING_LEVEL

echo "Airflow Variables set successfully:"
echo "  PROJECT_HOME = $PROJECT_ROOT"
echo "  VENV = $VENV_NAME"
echo "  CONFIG_PATH = $PROJECT_ROOT/configs/pipeline_config.yaml"
echo "  VENV_PATH = $VENV_PATH"

echo "-------------------------------------------------------"
echo "Double Check the Variables Above Before Using Airflow"  
echo "-------------------------------------------------------"

# -------------------------------
# 5. MLFLOW
# -------------------------------
echo "Starting MLflow server..."
nohup mlflow ui --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &
echo "MLflow server started in the background. Logs are being written to mlflow.log at $PROJECT_ROOT"
echo "PS NOTE >> Make sure to kill the port 5000 after the airflow orchestration is completed" 

echo "ashrae_pipeline_dag.py now should be available in your dags folder at: $AIRFLOW_DAGS_DIR for pipeline orchestration"  
echo "Setup completed successfully"