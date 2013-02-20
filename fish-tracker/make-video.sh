#!/bin/sh

cd output 
ffmpeg -qscale 10 -r 20 -b 9600 -i '%04d'.jpg ../output.mp4
cd ..
