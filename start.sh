#!/bin/bash
cd ~/destination_dispatch_touch_screen 
git pull &>> ~/ddt.git.log

python main.py &>> ~/ddt.log 

