#!/bin/bash
cd ~/destination_dispatch_touch_screen 
git pull &>> ~/ddt.git.log
export FULL_SCREEN=1
python main.py &>> ~/ddt.log 

