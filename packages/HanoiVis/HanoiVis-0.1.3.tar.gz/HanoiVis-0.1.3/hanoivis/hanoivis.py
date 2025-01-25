#!/usr/bin/env python3

import time
import curses
import argparse

parser = argparse.ArgumentParser(
    prog = "hanoivis",
    description = "Displays a step-by-step visualiser for the Tower of Hanoi puzzle",
    argument_default = argparse.SUPPRESS
)
parser.add_argument("-n", "--number", action="store", help = "Specifies the number of total disks")
parser.add_argument("-t", "--time", action="store", help = "Specifies the amount of time between each step")
args = parser.parse_args()

try:
    num_disks = int(args.number)
except AttributeError:
    num_disks = 5
try:
    sleep_time = float(args.time)
except AttributeError:
    sleep_time = 1

rod1 = []
rod2 = []
rod3 = []
count = -1

def print_hanoi(r1, r2, r3, stdscr):
    stdscr.clear()

    global count
    count += 1

    visual = []
    r1.reverse()
    r2.reverse()
    r3.reverse()
    
    # Rod 1
    n_blanks = num_disks - len(r1)
    for i in range (n_blanks):
        visual.append("\t|\t")
    
    for index, i in enumerate(r1):
        visual.append(f"\t{i}\t")
    
    # Rod 2
    n_blanks = num_disks - len(r2)
    for i in range(n_blanks):
        visual[i] += ("\t|\t")

    for index, i in enumerate(r2):
        visual[index + n_blanks] += f"\t{i}\t"
   
    # Rod 3
    n_blanks = num_disks - len(r3)
    for i in range(n_blanks):
        visual[i] += ("\t|\t")
    
    for index, i in enumerate(r3):
        visual[index + n_blanks] += f"\t{i}\t"
    
    for i, line in enumerate(visual):
        stdscr.addstr(i, 0, line)

    stdscr.addstr(len(visual), 0, f"\nMoves: {count}\n")
    stdscr.refresh()

    r1.reverse()
    r2.reverse()
    r3.reverse()

def move(start, end, stdscr):
    match start:
        case 1:
            item = rod1.pop(-1)
        case 2:
            item = rod2.pop(-1)
        case 3:
            item = rod3.pop(-1)
            
    
    match end:
        case 1:
            rod1.append(item)
        case 2:
            rod2.append(item)
        case 3:
            rod3.append(item)

    time.sleep(sleep_time)
    print_hanoi(rod1, rod2, rod3, stdscr)

def hanoi(n, start, end, stdscr):
    if n == 1:
        move(start, end, stdscr)
    else:
        other = 6 - (start + end)
        hanoi(n - 1, start, other, stdscr)
        move(start, end, stdscr)
        hanoi(n - 1, other, end, stdscr)

def main(stdscr):
    for i in range(num_disks, 0, -1):
        rod1.append(i)

    print_hanoi(rod1, rod2, rod3, stdscr)

    hanoi(num_disks, 1, 3, stdscr)
    stdscr.getkey()

curses.wrapper(main)
