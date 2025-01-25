import typer

from .lucidate import lucidate

app = typer.Typer()
app.command()(lucidate)

if __name__ == "__main__":
    app()