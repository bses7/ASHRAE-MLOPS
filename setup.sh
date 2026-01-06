#!/bin/bash
set -e

# =====================================================
# 1. Conda Environment Setup
# =====================================================
echo "--------------------------------"
echo "--- Conda Environment Setup ---"
echo "--------------------------------"

if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Install Miniconda/Anaconda first."
    exit 1
fi

# Initialize conda for non-interactive shells
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

echo "Do you want to create a new Conda environment or use an existing one?"
echo "1) Create a new environment (recommended)"
echo "2) Use an existing environment"
echo "Recommended: Create a new environment to avoid dependency conflicts."

read -p "Selection (1 or 2): " ENV_CHOICE
read -p "Enter Conda environment name: " VENV_NAME

VENV_PATH="${CONDA_BASE}/envs/${VENV_NAME}/bin/python"

case "$ENV_CHOICE" in
  1)
    if conda info --envs | grep -q -w "$VENV_NAME"; then
        echo "ERROR: Environment '$VENV_NAME' already exists."
        exit 1
    fi

    echo "Creating Conda environment '$VENV_NAME'..."
    conda create -y -n "$VENV_NAME" python=3.11.13

    echo "Activating environment..."
    conda activate "$VENV_NAME"

    if [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "WARNING: requirements.txt not found."
    fi
    ;;

  2)
    if ! conda info --envs | grep -q -w "$VENV_NAME"; then
        echo "ERROR: Environment '$VENV_NAME' does not exist."
        conda env list
        exit 1
    fi

    echo "Activating existing environment '$VENV_NAME'..."
    conda activate "$VENV_NAME"
    ;;

  *)
    echo "Invalid selection."
    exit 1
    ;;
esac

# =====================================================
# 2. Verify Environment (CRITICAL)
# =====================================================
echo "--------------------------------"
echo "Verifying Conda Environment"
echo "--------------------------------"

echo "Active environment: $CONDA_DEFAULT_ENV"
echo "Python executable: $(which python)"
python --version

if [[ "$CONDA_DEFAULT_ENV" != "$VENV_NAME" ]]; then
    echo "ERROR: Conda environment not active!"
    exit 1
fi

echo "Environment verification passed"

# =====================================================
# 3. Docker Setup (DB + Metabase)
# =====================================================
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

# =====================================================
# 4. Airflow Setup
# =====================================================
echo "--------------------------------"
echo "Configuring Airflow..."
echo "--------------------------------"

if [ -z "$AIRFLOW_HOME" ]; then
  export AIRFLOW_HOME="$HOME/airflow"
  echo "AIRFLOW_HOME set to $AIRFLOW_HOME"
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

# =====================================================
# 5. Airflow Variables
# =====================================================
echo "Setting Airflow Variables..."

export PYTHONWARNINGS="ignore::FutureWarning"
export AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR

airflow variables set PROJECT_HOME "$PROJECT_ROOT"
airflow variables set VENV "$VENV_NAME"
airflow variables set CONFIG_PATH "$PROJECT_ROOT/configs/pipeline_config.yaml"
airflow variables set VENV_PATH "$VENV_PATH"

unset PYTHONWARNINGS
unset AIRFLOW__LOGGING__LOGGING_LEVEL

echo "Airflow variables set successfully"

echo "Airflow Variables set successfully:" 
echo " PROJECT_HOME = $PROJECT_ROOT" 
echo " VENV = $VENV_NAME" 
echo " CONFIG_PATH = $PROJECT_ROOT/configs/pipeline_config.yaml" 
echo " VENV_PATH = $VENV_PATH"

# =====================================================
# 6. MLflow Setup
# =====================================================
echo "--------------------------------"
echo "Starting MLflow server..."
echo "--------------------------------"

nohup mlflow ui \
  --host 0.0.0.0 \
  --port 5000 \
  > "$PROJECT_ROOT/mlflow.log" 2>&1 &

echo "MLflow started (PID: $!)"
echo "Logs: $PROJECT_ROOT/mlflow.log"
echo "NOTE: Kill port 5000 after Airflow run if needed"

# # =====================================================
# # 7. Application Containers
# # =====================================================
# echo "--------------------------------"
# echo "Starting Application Containers..."
# echo "--------------------------------"

# docker-compose -f docker-compose-app.yaml up -d

# =====================================================
# 8. Final Info
# =====================================================
echo "-------------------------------------------------------"
echo "SETUP COMPLETED SUCCESSFULLY"
echo "-------------------------------------------------------"
echo "Active Conda Env : $VENV_NAME"
echo "MLflow UI        : http://127.0.0.1:5000"
echo "Airflow DAG Dir  : $AIRFLOW_DAGS_DIR"
echo "-------------------------------------------------------"

echo "PS NOTE: ashrae_pipeline_dag.py now should be available in your dags folder at: $AIRFLOW_DAGS_DIR for pipeline orchestration"

echo "-------------------------------------------------------"
echo "READY FOR PIPELINE RCHESTRATION SUCCESSFULLY"
echo "-------------------------------------------------------"
