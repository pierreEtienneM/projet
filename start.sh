#!/bin/bash

pythonCommand="python3"

$pythonCommand single.py &>/dev/null
mpiexec -n 5 $pythonCommand multi.py &>/dev/null

echo "Output Single"
sed '40q;d' outputSingle.txt

echo "Output Multi"
sed '40q;d' outputMulti.txt