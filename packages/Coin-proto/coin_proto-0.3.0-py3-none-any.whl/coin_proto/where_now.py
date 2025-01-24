import typer


def add(a, b):
    return a + b


def add_function():
    r = add(1,2)
    print(r)

def entry_point():
    typer.run(add_function)
