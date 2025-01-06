import glob
import os
from typing import Any

import ruamel.yaml as yaml

class SparkConfigGenerator:

    def get_spark_yml_files(self, job_dir: str) -> list[str]:
        """
        Recursively searches for all spark configs in repository
        :param job_dir: str
        :return: list[str]
        """
        return sorted([f for f in glob.glob(f'{job_dir}/**/.spark/config.yml', recursive=True) if os.path.getsize(f) > 0])

    def get_spark_python_files(self, config_path: str) -> list[str]:
        """
        Recursively searches for python spark job files
        :param config_path: str
        :return: list[str]
        """
        return sorted([f for f in glob.glob(f'{config_path}/*.py', recursive=True) if os.path.getsize(f) > 0])

    def generate_spark_yml(self) -> None:
        """
        Generates spark config containing all jobs
        :return: None
        """
        with open(os.path.join(os.path.dirname(__file__), 'anchors.yml'), 'r') as anchors_file:
            raw_file = anchors_file.read()

        raw_config = dict(yaml.round_trip_load(raw_file))

        # dev updates
        if os.environ.get('BUILD_DEV', '0') == '1':
            for i, anchor in enumerate(raw_config['anchors']):
                if 'spark.pie.kubernetes.driver.priorityClassName' in anchor:
                    anchor['spark.pie.kubernetes.driver.priorityClassName'] = 'p3'
                if 'spark.pie.kubernetes.executor.priorityClassName' in anchor:
                    anchor['spark.pie.kubernetes.executor.priorityClassName'] = 'p3'
                if 'spark.pie.driverEnv.KUBERNETES_SERVICE_HOST' in anchor:
                    anchor['spark.pie.driverEnv.KUBERNETES_SERVICE_HOST'] = 'kube-api.us-west-3d.aci.apple.com'
                if 'spark.pie.kubernetes.sdr.appname' in anchor:
                    anchor['spark.pie.kubernetes.sdr.appname'] = 'xoxhtzanezxptyqfvgjn'
                raw_config['anchors'][i] = anchor
            raw_config['triggers'] = []

        spark_config: dict[str, Any] = {"jobs": []}

        base_dir = os.path.abspath(os.path.join(os.getcwd(), 'jobs'))
        for f in self.get_spark_yml_files(base_dir):
            # get job name from job python file
            python_job_name = "/".join(self.get_spark_python_files(config_path="/".join(f.split("/")[:-2]))[0].split("/")[-4:])
            with open(f, 'r') as in_file:
                file_content = in_file.read()
                raw_jobs = dict(yaml.round_trip_load(file_content))

                # get default_config
                job_config: dict[str, Any] = {
                    "name": python_job_name.split("/")[-3] + '-' + python_job_name.split("/")[-1].replace(".py", "").replace("_", "-"),
                    "job_class": "/mnt/app/" + python_job_name,
                    "runtime_versions": {
                        "spark_version": "3.4.0"
                    },
                    "properties": dict(raw_config.get("anchors", [])[-1])
                }

                # add job details
                for key, value in raw_jobs.get("properties", {}).items():
                    job_config["properties"][key] = value
                spark_config["jobs"].append(job_config)

        os.makedirs(os.path.join(os.getcwd(), 'pie-config', 'platform'), exist_ok=True)

        with open(os.path.abspath(
                os.path.join(os.getcwd(), 'pie-config', 'platform', 'spark.yml')), 'w') as out_file:
            yaml.round_trip_dump(spark_config, out_file)
