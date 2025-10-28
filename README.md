# Raspberry Pi Playground

This repository contains a collection of Python experiments and projects designed for use with a Raspberry Pi. It serves as a space for learning, prototyping, and tinkering with various ideas and hardware integrations.

## Setup

First install the necessary apt packages:
```bash
sudo apt update
sudo apt install -y libcap-dev libatlas-base-dev ffmpeg libopenjp2-7 libcamera-dev libkms++-dev libfmt-dev libdrm-dev
```

To set up the repository and manage dependencies, use [`uv`](https://github.com/astral-sh/uv):
```bash
uv venv --python 3.11 --prompt raspi-playground --system-site-packages .venv
uv sync
```

## Running programs
We'll even use `uv` to run the programs, so that they use the virtual environment:
```bash
uv run src/main/raspi_playground/basics/stoplight.py
```

## Running Interactively
You can also run Python interactively with the virtual environment:
```bash
❯ uv run ipython
Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0]
Type 'copyright', 'credits' or 'license' for more information
IPython 9.5.0 -- An enhanced Interactive Python. Type '?' for help.
Tip: Put a ';' at the end of a line to suppress the printing of output.

In [1]: from gpiozero import LED

In [2]: led = LED(2)

In [3]: led.on()
```

