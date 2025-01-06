import glob
import os
import uuid

from amp_ds_platform_library.git.git_cli_operator import GitCLIOperator  # type: ignore
import ruamel.yaml as yaml
import typer


class JobCreate:

    def __init__(self, job_name: str):
        self.job_name = job_name

    def create_job(self) -> None:
        """Job creation workflow.

        :return: None
        """
        self.create_job_spark_config()
        self.push_changes_to_dev_branch()

    def create_job_spark_config(self) -> None:
        """Create individual job spark config file.

        :return: None
        """
        base_jobs_repo_dir = os.path.abspath(os.getcwd())

        found_jobs = self.search_job_file_by_name(directory=base_jobs_repo_dir, job_name=self.job_name)
        if len(found_jobs) > 1:
            typer.echo("Multiple jobs with the same name found.")
            raise typer.Exit(1)
        elif len(found_jobs) == 0:
            typer.echo("No jobs matching the required name found.")
            raise typer.Exit(1)

        job_folder = "/".join(found_jobs[0].split("/")[:-1])
        os.makedirs(os.path.join(job_folder, '.spark'), exist_ok=True)

        if os.path.isfile(os.path.join(job_folder, '.spark', 'config.yml')):
            typer.echo("Spark config file already exists for desired job. "
                       "If you wish to proceed, delete the config first.")
            raise typer.Exit(1)

        spark_config = {"uuid": str(uuid.uuid4())}
        with open(os.path.join(job_folder, '.spark', 'config.yml'), 'w') as out_file:
            yaml.round_trip_dump(spark_config, out_file)

    def push_changes_to_dev_branch(self) -> None:
        """Execute clean branch creation from main and push new jot changes.

        :return: None
        """
        dev_branch_name = f"dev-{self.job_name}-job"

        """1. Checkout to main branch"""
        GitCLIOperator().checkout_branch(branch_name="main")

        """2. Pull from main branch"""
        GitCLIOperator().pull(branch_name="main")

        """3. Checkout to dev branch"""
        GitCLIOperator().checkout_branch(branch_name=dev_branch_name, new_branch=True)

        """4. Commit changes"""
        GitCLIOperator().commit(commit_message=f"Create {self.job_name} job")

        """5. Push changes to branch"""
        GitCLIOperator().push(branch_name=dev_branch_name)

    @staticmethod
    def search_job_file_by_name(directory: str, job_name: str) -> list[str]:
        """Recursively searches for python spark job file by name.

        :param directory: directory where files are searched
        :param job_name: job name that's searched for
        :return: list[str]
        """
        return sorted([f for f in glob.glob(f'{directory}/**/{job_name}.py', recursive=True) if os.path.getsize(f) > 0])
