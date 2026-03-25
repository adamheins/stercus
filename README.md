# Stercus
Stercus is a simple language. Programs are written to operate on a pre-defined
block of memory, similar to brainfuck. The memory block is arbitrarily-sized
and can be set when compiling a program.

Stercus is very simple and impractical, and therefore provides an interesting
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

* `<number>`: A signed 8-bit value; that is, number from -128 to 127. Assigns
  the byte in the memory to the value of the number.
* `.`: Output the value stored in this memory location as an int.
* `:`: Output the value stored in this memory location as a char.
* `,`: Input a value and store it in this memory location.
* `+`: Increment the value stored in this memory location.
* `-`: Decrement the value stored in this memory location.

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

The ordering of applications in a file does not matter: applications can
reference any other applications in the same file.

#### Variables

One use of custom applications is to create named values:
```
# assign 'a' to have a value 5
{a [$ 5]}  

# now I can assign the value of 'a' to other bytes
# e.g., assign the value of 'a' (5) to byte 3:
[3 a]

# I can also assign the value of 'a' to other "variables":
{b [$ a]}
```

## Compilation

Stercus files typically end with a `.cus` extension. Stercus files can be
compiled using the `stercusc` executable installed with this package. By
default, the compiler produces C source files, which can then be compiled with
your C compiler of choice. You can use the `-c` flag to pass a C compiler
command to automatically compile the C code as well. Examples:
```
stercusc example.cus  # produces `example.c`

# use a memory array of 100 bytes (default is 10,000)
stercusc example.cus -m 100

# pass a command to compile to C file as well (e.g. using gcc)
stercusc example.cus -c gcc  # produces `example` binary

# the above command is equivalent to:
stercusc example.cus
gcc example.c -o example
```

## Bounds Checking

`stercusc` can identify some out-of-bounds memory accesses when compiling, in
which case it will raise an error and abort. Other out-of-bounds errors are
checked at runtime; if access to an out-of-bounds element of the memory array
is attempted, a warning is printed. If retrieving the element's value, zero
will be returned instead; if setting the value, nothing is done.

## Command Line Arguments

A binary compiled with `stercusc` and a C compiler automatically loads the
provided CLI arguments into the initial bytes of its memory array (unlike other
programs, the program name itself is not included). For example
```
# suppose I have the executable called `example` from above and I run
./example foo bar

# then the first 7 bytes of example's memory array are (the numeric
# representations of): ['f', 'o', 'o', ' ', 'b', 'a', 'r']
```

## Tools

* The `text2stercus` executable converts text to the stercus expression for
  outputting that string of text.

## Examples
Additional example stercus programs may be found in the `examples/` directory.

## License
MIT license. See the LICENSE file.
