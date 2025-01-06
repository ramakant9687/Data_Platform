from amp_ds_platform_cli.job.create import JobCreate
import typer


app = typer.Typer()


@app.command()
def create(job_name: str) -> None:
    """Typer command used to create jobs.

    :param job_name: str
    :return: None
    """
    JobCreate(job_name=job_name).create_job()


if __name__ == "__main__":
    app()
