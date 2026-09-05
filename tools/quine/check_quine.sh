#!/bin/sh
uv run stercusc quine.cus -d int -c gcc
./quine > /tmp/quine.out
diff -sq quine.cus /tmp/quine.out
