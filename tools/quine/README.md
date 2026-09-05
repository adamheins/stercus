# Stercus Quine

Generate a [quine](https://en.wikipedia.org/wiki/Quine_(computing)) written in
stercus (this is the same one in the examples directory):
```
# generate_quine.py was written by Claude Opus 5
# generates quine.cus
uv run python generate_quine.py
```

Compile and verify:
```
# generates quine binary
uv run stercusc quine.cus -d int -c gcc

# run and capture output
./quine > /tmp/quine.out

# compare to the source code
diff -sq quine.cus /tmp/quine.out
```
