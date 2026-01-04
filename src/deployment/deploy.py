import subprocess
import os
import stat
from src.common.logger import get_logger

class DeploymentOrchestrator:
    def __init__(self):
        self.logger = get_logger("DeploymentOrchestrator")
        self.deploy_script = "deployment/deploy.sh"

    def _ensure_executable(self):
        """Ensures the shell script has execution permissions."""
        st = os.stat(self.deploy_script)
        os.chmod(self.deploy_script, st.st_mode | stat.S_IEXEC)

    def run_deployment(self):
        self.logger.info("Starting production deployment sequence...")
        
        try:
            self._ensure_executable()
            
            result = subprocess.run(
                [f"./{self.deploy_script}"],
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info("Deployment script output:\n" + result.stdout)
            self.logger.info("Successfully deployed Backend and Frontend containers.")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed! Error output:\n{e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during deployment: {e}")
            raise

def run_deployment_stage():
    orchestrator = DeploymentOrchestrator()
    orchestrator.run_deployment()