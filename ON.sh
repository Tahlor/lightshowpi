#!/bin/bash

# 2,1,0,16,15,7,9,8
# gpio blink 0
# for some reason, I needed to blink each GPIO pin before `gpio write` would work??

for ((i=0; i<=18; i++)); do
    echo $i
    gpio write $i 1
done;

