import typer

def hha():
    return "Nice Spending"

def print_hha():
    r = hha()
    print(r)

def entry_point():
    typer.run(print_hha)
