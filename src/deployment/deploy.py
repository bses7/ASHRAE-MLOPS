import subprocess
import os
import stat
from pathlib import Path
from src.common.logger import get_logger

class DeploymentOrchestrator:
    def __init__(self):
        self.logger = get_logger("DeploymentOrchestrator")
        
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
        self.deploy_script = self.project_root / "src"/ "deployment" / "deploy.sh"

    def _ensure_executable(self):
        """Ensures the shell script has execution permissions."""
        if not self.deploy_script.exists():
            raise FileNotFoundError(f"Deploy script not found at {self.deploy_script}")
            
        st = os.stat(self.deploy_script)
        os.chmod(self.deploy_script, st.st_mode | stat.S_IEXEC)

    def run_deployment(self):
        self.logger.info(f"Starting production deployment from root: {self.project_root}")
        
        try:
            self._ensure_executable()

            result = subprocess.run(
                [str(self.deploy_script)],
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.project_root) 
            )
            
            self.logger.info("Deployment script output:\n" + result.stdout)
            self.logger.info("Successfully deployed Backend and Frontend containers.")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed! Error output:\n{e.stderr}")
            self.logger.error(f"Stdout output:\n{e.stdout}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during deployment: {e}")
            raise

def run_deployment_stage():
    orchestrator = DeploymentOrchestrator()
    orchestrator.run_deployment()