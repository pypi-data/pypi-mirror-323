import typer
import random

def today_num(i: int,k:int):
    a = random.randint(i,k)
    print(a)
    return a

def entry_point():
    typer.run(today_num)    
