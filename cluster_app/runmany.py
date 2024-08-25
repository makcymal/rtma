import os
import subprocess
import randomname as rn
from random import choice


if __name__ == "__main__":
    sensors = []
    N = 20

    batches = [
        rn.get_name(adj=("size", "materials"), noun=("infrastructure",))
        for i in range(5)
    ]
    labels = [
        rn.get_name(
            noun=("astronomy", "minerals", "ghosts", "music_instruments", "water"),
        )
        for i in range(N)
    ]

    with open("runmany.log", 'w') as log:
        for i in range(N):
            batch = choice(batches)
            label = labels[i]
            subprocess.call(["D:/Projects/rtma/.venv/Scripts/python.exe", "runcluster.py",  batch, label])
            print(f"{batch}!{label} is running with pid {sp.pid}", file=log)
    