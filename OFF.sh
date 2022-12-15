#!/bin/bash

for ((i=0; i<=18; i++)); do
    echo $i
    gpio write $i 0

done;

