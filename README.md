# Stercus
Stercus is a simple language. Programs are written to operate on a pre-defined
block of memory, similar to brainfuck. The memory block is arbitrarily-sized;
the current compiler uses a block of 10,000 bytes.

Stercus is also ridiculous. It is esoteric and creating a program of any
notable size is very diffcult. However, it does provide an interesting
challenge: create a meaningful program with an _extremely_ limited toolset. The
word "meaningful" is being used loosely here.

## Applicators
The memory is random-accessed using __applicators__. Applicators "apply" an
application to a byte of memory. An applicator is denoted by square brackets
(`[]`), and takes the form
```
[<index> <applications>]
```
The `<index>` is the index of the byte in memory to act on (memory is
zero-indexed). Following this is a list of applications to apply to the byte at
this memory location. Applications are delimited by whitespace.

There is no limit to the number of applications applied in a single applicator.
Applicators return the value stored at the memory location which they are
acting on, after all applicators have been applied. Applicators may be used
without any applications to just return the value at a memory location.
```
# Apply the increment application (+), to the 0th byte.
[0 +]

# Assign a value of 10 to byte 1.
[1 10]

# Assign the value of byte 1 to byte 2.
[2 [1]]
```

## Conditionals
Conditional statements and loops are written using round brackets (`()`). They
take the form
```
(<index> <body>)
```
The `<index>` is the index of the byte in memory to test. If this byte is not
0, the conditional satement is executed. The conditional statement will keep
looping until the byte obtains a value of 0. Following this is the `<body>` of
the conditional, which can consist of any number of applicators and other
conditionals.
```
# Only execute if byte 1 != 0
(1 [0 +])

# Loop 5 times
[0 5]
(0 [0 -])
```

## Applications
__Applications__ act on bytes in the memory block. There are a number of
built-in applications, and custom ones can be programmed. Applications are
similar to functions in other languages, except that they take no explicit
arguments and do not explicitly return values. Applications are implicitly
passed the location of the byte in memory on which they are acting.

### Built-in Applications
The built-in applications are:

`<number>`: A number from 0 to 127. Assigns the byte in the memory to the value
of the number. Attempting to use a number outside of 0 to 127 results in
undefined behaviour.

`.`: Output the value stored in this memory location.

`,`: Input a value and store it in this memory location.

`+`: Increment the value stored in this memory location.

`-`: Decrement the value stored in this memory location.

### Custom Applications
Custom applications are denoted by curly brackets (`{}`). The application takes
the form
```
{<name> <body>}
```
The `<name>` is the name of the application and must be unique. The application
body is just regular stercus code, acting on the globally-accessible memory.
The index of the byte to which the application is being applied is held in the
special `$` variable.  This variable only exists within applications and may
not be reassigned.
```
# A custom application that just increments the byte it is applied to by 2.
{foo [$ + +]}
```

The ordering of applications in a file does not matter. Applications can
reference other applications that are declared textually beneath them in the
file.

## Compilation
Stercus files typically end with a `.cus` extension. Stercus files can be
compiled using the `stercusc` executable in the `compiler/` directory. The
compiler produces C source files, which can then be compiled with your C
compiler of choice.

## Tools
Additional tools may be found in the `tools/` directory.
* text2stercus.py: Convert text to the stercus expression for outputting that
  string of text.

## Examples
Additional example stercus programs may be found in the `examples/` directory.

## License
MIT license. See the LICENSE file.
