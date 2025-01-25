
from pathlib import Path
import typer
from ..content.cli_content import *
from ..function.check_class import check_class
from ..function.check_app import check_app
from ..function.basic import make_controller, make_model, make_routes, make_service, make_validator

app= typer.Typer()


@app.command("make:controller")
def controller(name: str, app_name: str , 
               v: bool=typer.Option(False,help=f"for Creating the Validator you can pass S. S mean { typer.style("Validator",typer.colors.YELLOW,bold=True) }   "),
               s: bool=typer.Option(False,help=f"for Creating the Service you can pass S. S mean  { typer.style("Service",typer.colors.GREEN,bold=True) } "),
               m: bool=typer.Option(False,help=f"for Creating the Model you can pass M. M mean Model { typer.style("Model",typer.colors.BRIGHT_RED,bold=True) } "),
               r: bool=typer.Option(False,help=f"for Creating the all Routes you can pass S. S mean  { typer.style("Resource",typer.colors.BRIGHT_BLUE,bold=True) } ")):
    
    """
    Generate a FastAPI controller file with a user-defined name inside a specific app.
    """
    if(m):
        print(m,s,r)

    make_controller(name=name,app_name=app_name)
    if(m):
        make_model(name=name,app_name=app_name)
    if(s):
        make_service(name=name,app_name=app_name)
    if(v):
        make_validator(name=name,app_name=app_name)
    if(r):
        make_routes(name=name,app_name=app_name)

@app.command("make:model")
def model(name: str, app_name: str , 
               v: bool=typer.Option(False,help=f"for Creating the Validator you can pass S. S mean { typer.style("Validator",typer.colors.YELLOW,bold=True) }   "),
               s: bool=typer.Option(False,help=f"for Creating the Service you can pass S. S mean  { typer.style("Service",typer.colors.GREEN,bold=True) } "),
               c: bool=typer.Option(False,help=f"for Creating the Controller you can pass C. C means  { typer.style("Controller",typer.colors.YELLOW,bold=True) } "),
               r: bool=typer.Option(False,help=f"for Creating the all Routes you can pass S. S mean  { typer.style("Resource",typer.colors.BRIGHT_BLUE,bold=True) } ")):
    """
    Generate a Beanie ODM model file with a user-defined name inside a specific app.
    """
    
    make_model(name=name,app_name=app_name)
    if(c):
        make_controller(name=name,app_name=app_name)
    if(s):
        make_service(name=name,app_name=app_name)
    if(v):
        make_validator(name=name,app_name=app_name)
    if(r):
        make_routes(name=name,app_name=app_name)



@app.command("make:validator")
def validator(name: str, app_name: str , 
               c: bool=typer.Option(False,help=f"for Creating the Controller you can pass C. C means { typer.style("Controller",typer.colors.BRIGHT_YELLOW,bold=True) } "),
               s: bool=typer.Option(False,help=f"for Creating the Service you can pass S. S mean  { typer.style("Service",typer.colors.YELLOW,bold=True) } "),
               m: bool=typer.Option(False,help=f"for Creating the Model you can pass M. M mean Model { typer.style("Service",typer.colors.BRIGHT_RED,bold=True) } "),
               r: bool=typer.Option(False,help=f"for Creating the all Routes you can pass S. S mean  { typer.style("Resource",typer.colors.BRIGHT_RED,bold=True) } ")):
    """
    Generate a Pydantic validator file with a user-defined name inside a specific app.
    """
    make_validator(name=name,app_name=app_name)
    if(c):
        make_controller(name=name,app_name=app_name)
    if(s):
        make_service(name=name,app_name=app_name)
    if(m):
        make_model(name=name,app_name=app_name)
    if(r):
        make_routes(name=name,app_name=app_name)

@app.command("make:service")
def service(name: str, app_name: str , 
               v: bool=typer.Option(False,help=f"for Creating the Validator you can pass S. S mean { typer.style("Validator",typer.colors.YELLOW,bold=True) }   "),
               m: bool=typer.Option(False,help=f"for Creating the Model you can pass M. M mean  { typer.style("Model",typer.colors.GREEN,bold=True) } "),
               c: bool=typer.Option(False,help=f"for Creating the Controller you can pass C. C means  { typer.style("Controller",typer.colors.YELLOW,bold=True) } "),
               r: bool=typer.Option(False,help=f"for Creating the all Routes you can pass S. S mean  { typer.style("Resource",typer.colors.BRIGHT_BLUE,bold=True) } ")):
    """
    Generate a service class file with a user-defined name inside a specific app.
    """
    make_service(name=name,app_name=app_name)
    if(c):
        make_controller(name=name,app_name=app_name)
    if(m):
        make_model(name=name,app_name=app_name)
    if(v):
        make_validator(name=name,app_name=app_name)
    if(r):
        make_routes(name=name,app_name=app_name)


@app.command("make:middleware")
def make_middleware(name: str,app_name:str):
    """
    Generate a middleware file with a user-defined name inside a specific app.
    """
    # Directory paths
    middleware_folder = app_name/"/middleware"
    app_dir = check_app(app_name=app_name)
    middleware_dir = app_dir / middleware_folder

    # Capitalize the middleware name and generate file name
    class_name = f"{name.capitalize()}Middleware"
    file_name = f"{name.lower()}_middleware.py"
    file_path = middleware_dir / file_name

    # Check if the middleware file already exists
    check_class(file_path=file_path, app_name=app_name, class_name=class_name)

    # Middleware boilerplate content
    content = get_middleware_content(name=name, app_name=app_name)

    # Ensure the middleware directory exists
    middleware_dir.mkdir(parents=True, exist_ok=True)

    # Write the middleware file
    file_path.write_text(content)
    typer.echo(f"Middleware '{class_name}' created successfully in '{file_path}'!")


@app.command("make:seeder")
def make_seeder(name: str,app_name:str):
    """
    Generate a seeder file with a user-defined name inside a specific app.
    """
    # Directory paths
    seederfolder="database"
    app_dir = check_app(app_name=seederfolder)
    middleware_dir = app_dir / "seeders"

    # Capitalize the seeder name and generate file name
    class_name = f"{name.capitalize()}Seeder"
    file_name = f"{name.lower()}_seeder.py"
    file_path = middleware_dir / file_name

    # Check if the seeder file already exists
    check_class(file_path=file_path, app_name=app_name, class_name=class_name)

    # Middleware boilerplate content
    content = get_seeder_content(name=name,app_name=app_name)

    # Ensure the seeder directory exists
    middleware_dir.mkdir(parents=True, exist_ok=True)

    # Write the seeder file
    file_path.write_text(content)
    typer.echo(f"Seeder '{class_name}' created successfully in '{file_path}'!")


   
@app.command("make:routes")
def create_routes(name: str, app_name: str, routes: str):
    """
    Generate route file with user-defined routes inside a specific app.
    Routes should be passed as a  string.
    Example: 'GET,POST,PUT'
    """
    # make_routes(name, app_name, routes)


import socket
import typer

@app.command("runserver")
def run_server(
    mode: str = typer.Option(
        "dev", 
        help="Run mode: 'dev' for development or 'prod' for production",
        case_sensitive=False
    ),
    host: str = typer.Option("127.0.0.1", help="The host to bind the server to"),
    port: int = typer.Option(8000, help="The port to run the server on"),
    workers: int = typer.Option(1, help="Number of worker processes for the server"),
):
    """
    Run the FastAPI server in development ('dev') or production ('prod') mode with a specified number of workers.
    """
    def is_port_in_use(host: str, port: int) -> bool:
        """Check if the given port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except socket.error:
                return True

    def find_available_port(host: str, port: int) -> int:
        """Find the next available port."""
        while is_port_in_use(host, port):
            port += 1
        return port

    try:
        import uvicorn

        if mode.lower() not in ["dev", "prod"]:
            typer.echo("Invalid mode. Use 'dev' for development or 'prod' for production.", err=True)
            raise typer.Exit(code=1)

        reload = mode.lower() == "dev"
        environment = "Development" if reload else "Production"

        # Check if port is in use, if so, find an available one
        port = find_available_port(host, port)

        typer.echo(f"Starting server in {environment} mode at http://{host}:{port} with {workers} workers...")
        uvicorn.run("server:app", host=host, port=port, reload=reload, workers=workers)
        print("Server started.")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


    
