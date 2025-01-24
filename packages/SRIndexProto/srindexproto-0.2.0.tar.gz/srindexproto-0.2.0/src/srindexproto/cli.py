import random
import typer

def total_srindex(give_and_take: int, celebration:int , freq_call: int, freq_meeting:int):
    give_and_take = random.randrange(0, 100)
    celebraion = random.randrange(0, 100)
    freq_call = random.randrange(0, 100)
    freq_meeting = random.randrange(0, 100)

    raw_index = (give_and_take, celebration, freq_call, freq_meeting)
    return raw_index

def total_weight(t_weight1: int, t_weight2:int, t_weight3:int, t_weight4:int):
    t_weight1 = random.randrange(0, 1)
    t_weight2 = random.randrange(0, 1 - t_weight1)
    t_weight3 = random.randrange(0, 1 - t_weight1 - t_weight2)
    t_weight4 = random.randrange(0, 1 - t_weight1 - t_weight2 - t_weight3) 
    t_weight = (t_weight1, t_weight2, t_weight3, t_weight4)
    return t_weight

def print_srindex(give_and_take:int, celebration:int, freq_call:int, freq_meeting:int):
    print(total_srindex(give_and_take, celebration, freq_call, freq_meeting))

def print_weight(give_and_take:int, celebration:int, freq_call:int, freq_meeting:int):
    print(total_weight(t_weight1, t_weight2, t_weight3, t_weight4))

def entry_point():
    typer.run(print_srindex)

    



