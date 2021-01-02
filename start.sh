#!/bin/bash


cd ~/destination_dispatch_touch_screen 
git pull &>> ~/ddt.git.log
export FULL_SCREEN=
python3 main.py &>> ~/ddt.log

