import os
import threading
import time
import urllib.request
import logging
from datetime import datetime, timezone

from matrice.deploy.predictor.fastapi_predictor import MatriceFastAPIPredictor
from matrice.deploy.predictor.triton_predictor import MatriceTritonPredictor
from matrice.actionTracker import ActionTracker

class MatriceDeploy:

    def __init__(self, load_model:callable =None, predict:callable =None, action_id:str ="", external_port:int =80):

        self.actionTracker = ActionTracker(action_id)
        self.rpc = self.actionTracker.session.rpc

        self.action_details = self.actionTracker.action_details
        logging.info(f"Action details: {self.action_details}")

        self.deployment_instance_id = self.action_details["_idModelDeployInstance"]
        self.deployment_id = self.action_details["_idDeployment"]
        self.model_id = self.action_details["_idModelDeploy"]

        self.ip = self.get_ip()
        try:
            if "fastapi" in self.actionTracker.server_type.lower():
                self.predictor = MatriceFastAPIPredictor(load_model, predict, self.actionTracker)
                self.server_process = self.predictor.setup(external_port)
            elif "triton" in self.actionTracker.server_type.lower():
                self.predictor = MatriceTritonPredictor(self.actionTracker)
                self.server_process = self.predictor.setup(external_port)
            else:
                raise ValueError(f"Unsupported server type: {self.actionTracker.server_type}")
            self.update_deployment_address(int(external_port))
            self.actionTracker.update_status(
                "MDL_DPL_STR", "OK", "Model deployment started"
            )
        except Exception as e:
            logging.error(f"Failed to initialize server: {str(e)}")
            self.actionTracker.update_status(
                "ERROR", "ERROR", f"Model deployment error: {str(e)}"
            )
            raise

        self.deployed_start_time = datetime.now(timezone.utc)
        self.shutdown_threshold = (
            int(self.action_details.get("shutdownThreshold", 15)) * 60
        )
        self.auto_shutdown = self.action_details.get("autoShutdown", True)
        self.run_shutdown_checker()

    def get_ip(self):
        """Get the public IP address of the deployment"""
        try:
            external_ip = (
                urllib.request.urlopen("https://ident.me", timeout=10)
                .read()
                .decode("utf8")
            )
            logging.info(f"Public IP address: {external_ip}")
            return external_ip
        except Exception as e:
            logging.error(f"Failed to get public IP: {str(e)}")
            raise

    def is_instance_running(self):
        try:
            resp = self.rpc.get(f"/v1/deployment/{self.deployment_id}")
            if resp["success"]:
                running_nstances = resp["data"]["runningInstances"]
                for instance in running_nstances:
                    if instance["modelDeployInstanceId"] == self.deployment_instance_id:
                        if instance["deployed"]:
                            return True
                return False
            else:
                logging.error(f"Failed to get deployment instance: {resp['message']}")
                return False
        except Exception as e:
            logging.error(f"Failed to get deployment instance: {str(e)}")
            return False

    def get_elapsed_time_since_latest_inference(self):
        now = datetime.now(timezone.utc)
        try:
            latest_prediction_time = self.rpc.get(
                f"/v1/model_prediction/get_latest_prediction_time/{self.deployment_instance_id}"
            )
            if latest_prediction_time["success"]:
                last_time = datetime.strptime(
                    latest_prediction_time["data"],
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                ).replace(tzinfo=timezone.utc)
                return (now - last_time).total_seconds()
            else:
                logging.info(
                    f"Failed to get latest prediction time, will use the deployed start time: {latest_prediction_time['message']}"
                )
                return (now - self.deployed_start_time).total_seconds()
        except Exception as e:
            logging.error(f"Failed to get elapsed time: {str(e)}")
            raise

    def trigger_shutdown_if_needed(self):
        """Check idle time and trigger shutdown if threshold exceeded"""
        try:
            elapsed_time = self.get_elapsed_time_since_latest_inference()
            if (
                (elapsed_time > self.shutdown_threshold) and self.auto_shutdown
            ) or not self.is_instance_running():
                logging.info(
                    f"Idle time ({elapsed_time:.1f}s) exceeded threshold ({self.shutdown_threshold}s)"
                )
                self.shutdown()
            else:
                logging.info(f"Time since last inference: {elapsed_time:.1f}s")
                logging.info(
                    f"Time until shutdown: {self.shutdown_threshold - elapsed_time:.1f}s"
                )
        except Exception as e:
            logging.error(f"Error checking shutdown condition: {str(e)}")

    def shutdown(self):
        """Gracefully shutdown the deployment instance"""
        try:
            logging.info("Initiating shutdown sequence...")
            try:
                self.rpc.delete(
                    f"/v1/deployment/delete_deploy_instance/{self.deployment_instance_id}"
                )
            except Exception as e:
                logging.error(f"Failed to delete deployment instance: {str(e)}")
            try:
                if self.server_process:
                    self.server_process.kill()
            except Exception as e:
                logging.error(f"Failed to terminate server process: {str(e)}")

            self.actionTracker.update_status(
                "MDL_DPL_STP", "SUCCESS", "Model deployment stopped"
            )
            # Allow time for cleanup and status updates to complete
            time.sleep(10)
            os._exit(0)
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")
            os._exit(1)

    def shutdown_checker(self):
        """Background thread to periodically check for idle shutdown condition"""
        while True:
            try:
                self.trigger_shutdown_if_needed()
            except Exception as e:
                logging.error(f"Error in shutdown checker: {str(e)}")
            finally:
                time.sleep(10)

    def run_shutdown_checker(self):
        """Start the shutdown checker thread as a daemon"""
        checker_thread = threading.Thread(
            target=self.shutdown_checker, name="ShutdownChecker"
        )
        checker_thread.start()
        logging.info("Shutdown checker thread started")

    def update_deployment_address(self, external_port):
        """Update the deployment address in the backend"""
        payload = {
            "port": external_port,
            "ipAddress": self.ip,
            "_idDeploymentInstance": self.deployment_instance_id,
            "_idModelDeploy": self.deployment_id,
            "_idInstance": self.action_details["instanceID"],
        }

        try:
            resp = self.rpc.put(
                path="/v1/deployment/update_deploy_instance_address", payload=payload
            )
            logging.info(f"Updated deployment address to {self.ip}:{external_port}, response: {resp}")
        except Exception as e:
            logging.error(f"Failed to update deployment address: {str(e)}")
            raise
