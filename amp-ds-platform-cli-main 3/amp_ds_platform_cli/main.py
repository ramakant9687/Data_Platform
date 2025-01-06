from amp_ds_platform_cli.authentication.authentication import auth_callback
from amp_ds_platform_cli.job import job
import typer

app = typer.Typer()
app.callback()(auth_callback)
app.add_typer(job.app, name="job")


if __name__ == "__main__":
    app()
