"""
Developed in order to simplify integrating Sonarqube with RIO

Example RIO pipeline for a pull request

    machine:
      baseImage: docker.apple.com/base-images/ubi9/ubi-builder:latest
      env:
        PYTHON_VERSION: python-3.10.9-1
        RUNTIME_JDK_VERSION: 'jdk-11.0.4-applejdk-11.4-1'
        CIRCLECI: "true"
        PYTEST_PATH: ".out/test-results/pytest"
        FLAKE_PATH: ".out/test-results-sonar/flake8"
        COVERAGE_PATH: ".out/test-results-sonar/coverage"
        SONAR_PROJECT_KEY: <your sonarqube project name>
    secrets:
      names:
        - sonar_token
    build:
      template: freestyle:v4:prb
      steps:
        - eval $(ci install-runtime ${PYTHON_VERSION} ${RUNTIME_JDK_VERSION})
        - python -m venv .venv/build && source .venv/build/bin/activate
        - python -m pip install --upgrade pip
        - pip install build twine setuptools wheel toml
        - pip config set global.index-url https://pypi.apple.com/simple
        - pip install -e ".[dev,test]"
        - mkdir -p .out/test-results/mypy
        - mkdir -p PYTEST_PATH
        - mkdir -p COVERAGE_PATH
        - mkdir -p FLAKE_PATH
        - flake8 <main project directory> tests --format junit-xml --exit-zero --output-file $FLAKE_PATH/flake8.xml
        - pytest tests --junitxml=$PYTEST_PATH/pytest.xml --cov --cov-report=xml:$COVERAGE_PATH/coverage.xml
        - run_sonarqube --project_key $SONAR_PROJECT_KEY --pytest_report_path $PYTEST_PATH/pytest.xml --flake_report_path $FLAKE_PATH/flake8.xml --coverage_report_path $COVERAGE_PATH/coverage.xml
"""
import argparse
import os
import requests
import subprocess
import sys
import zipfile

import toml

sonar_config_opts = [
    "-Dsonar.host.url=https://amp-sonarqube.apple.com",
    "-Dsonar.sourceEncoding=UTF-8",
    "-Dsonar.filesize.limit=50",
    "-Dsonar.coverage.exclusions=tests/**/*",
    "-Dsonar.exclusions=tests/**/*",
    "-Dsonar.python.version=3.10",
]


def run_sonarqube_scan() -> None:
    """Function for using sonarqube scanner as entry point script with arguments.

    :param --project_key: SonarQube project key
    :param --pytest_report_path: Path to pytest results
    :param --flake_report_path: Path to flake results
    :param --coverage_report_path: Path to coverage results
    """
    parser = argparse.ArgumentParser(description='Run SonarQube scan')
    parser.add_argument('--project_key', type=str, required=True, help='SonarQube project key')
    parser.add_argument('--pytest_report_path', type=str, required=False, default="", help='Path to pytest results')
    parser.add_argument('--flake_report_path', type=str, required=False, default="", help='Path to flake results')
    parser.add_argument('--coverage_report_path', type=str, required=False, default="", help='Path to coverage results')
    # Add more arguments as needed

    # Parse the arguments passed from the command line
    args = parser.parse_args(sys.argv[1:])

    # Use the parsed arguments in your scan method
    SonarQubeOperator().perform_scan(
        sonar_config_project_key=args.project_key,
        pytest_report_path=args.pytest_report_path,
        flake_report_path=args.flake_report_path,
        coverage_report_path=args.coverage_report_path
    )


class SonarQubeOperator:

    def perform_scan(self, sonar_config_project_key: str, pytest_report_path: str = "",
                     flake_report_path: str = "", coverage_report_path: str = "") -> None:
        """Run SonarQube scanner."""
        # SonarQube scanner version, download details and config
        sonar_version = "4.7.0.2747"
        sonar_scanner_zip = f"sonar-scanner-cli-{sonar_version}-linux.zip"
        sonar_scanner = f"sonar-scanner-{sonar_version}-linux"

        build_secrets_path = os.environ.get("BUILD_SECRETS_PATH", "")
        rio_branch_name = os.environ.get("RIO_BRANCH_NAME")
        git_pr_id = os.environ.get("GIT_PR_ID")
        git_pr_source_branch = os.environ.get("GIT_PR_SOURCE_BRANCH")
        git_pr_target_branch = os.environ.get("GIT_PR_TARGET_BRANCH")

        sonar_config_opts.append(f"-Dsonar.projectKey={sonar_config_project_key}")
        if len(pytest_report_path) > 0:
            sonar_config_opts.append(f"-Dsonar.python.xunit.reportPath={pytest_report_path}")
        if len(flake_report_path) > 0:
            sonar_config_opts.append(f"-Dsonar.python.flake8.reportPaths={flake_report_path}")
        if len(coverage_report_path) > 0:
            sonar_config_opts.append(f"-Dsonar.python.coverage.reportPaths={coverage_report_path}")

        # Construct path to sonar token
        sonar_token_path = os.path.join(build_secrets_path, 'sonar_token')

        # Check if sonar token exists
        if not os.path.exists(sonar_token_path):
            raise RuntimeError("Sonar token not found. Skipping SonarQube scan.")

        # Read sonar token
        with open(sonar_token_path, 'r') as token_file:
            sonar_token = token_file.read().strip()

        # Download SonarQube scanner
        print("Downloading sonar-scanner-cli")
        download_url = (f"https://artifacts.apple.com/bintray-sonarsource-binaries-cache/"
                        f"Distribution/sonar-scanner-cli/{sonar_scanner_zip}")
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(sonar_scanner_zip, "wb") as file:
                for chunk in response.iter_content(chunk_size=16384):
                    file.write(chunk)

        # Unzip the scanner
        print("Unzipping sonar-scanner-cli")
        with zipfile.ZipFile(sonar_scanner_zip, 'r') as zip_ref:
            zip_ref.extractall('.')

        # Remove zip file
        os.remove(sonar_scanner_zip)

        os.chmod("sonar-scanner-4.7.0.2747-linux/bin/sonar-scanner", 0o755)
        os.chmod("sonar-scanner-4.7.0.2747-linux/jre/bin/java", 0o755)

        # Prepare run options
        run_opts = []
        project_version_opts = []

        # Determine scan configuration based on PR or branch
        if git_pr_id:
            print("Setting PRB-related environment variables")
            run_opts = [
                f"-Dsonar.pullrequest.key={git_pr_id}",
                f"-Dsonar.pullrequest.branch={git_pr_source_branch}",
                f"-Dsonar.pullrequest.base={git_pr_target_branch}"
            ]
        else:
            # For branch scan, set branch name
            run_opts = [f"-Dsonar.branch.name={rio_branch_name}"]

            project_version = self.extract_project_version()
            if len(project_version):
                project_version_opts = [f"-Dsonar.projectVersion={project_version}"]

        # Prepare sonar scanner command
        myenv = os.environ.copy()
        myenv['SONAR_SCANNER_OPTS'] = f'-Djavax.net.ssl.trustStore=/etc/pki/java/cacerts -Dsonar.login={sonar_token}'
        sonar_scanner_path = os.path.join(sonar_scanner, 'bin', 'sonar-scanner')
        sonar_command = [
            sonar_scanner_path,
            '-X'
        ] + run_opts + project_version_opts + sonar_config_opts

        # Execute sonar scanner
        print("Executing sonar-scanner")
        try:
            result = subprocess.run(sonar_command, check=True, capture_output=True, text=True, env=myenv)
            print("Sonar-scanner completed successfully")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Sonar-scanner failed:")
            print(e.stderr)

    @staticmethod
    def extract_project_version() -> str:
        """Extract the project version from various locations."""
        # Extract project version from env variable
        project_version = os.environ.get("PROJECT_VERSION", "")
        if len(project_version):
            return project_version

        # Extract project version from pyproject.toml
        try:
            pyproject = toml.load('pyproject.toml')
            project_version = pyproject['project']['version']
            if len(project_version):
                return project_version
        except Exception:
            pass

        # Extract project version from version
        try:
            with open('version', 'r') as version_file:
                project_version = version_file.read().strip()
                if len(project_version):
                    return project_version
        except Exception:
            pass

        # If everything fails, return empty string
        return ""
