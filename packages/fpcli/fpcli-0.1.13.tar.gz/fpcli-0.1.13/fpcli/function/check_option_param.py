import typer


def check_option_paramas(params:typer.Option(help="here option params will come according the userinput")):
    print(params)
    