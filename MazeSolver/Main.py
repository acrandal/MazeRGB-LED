#!/usr/bin/env python3


from Cell import Cell


if __name__ == "__main__":
    print("running")

    c = Cell(4, 7, 0)
    c2 = Cell(4, 7, 1)
    print(c)

    if(c < c2):
        print("less")