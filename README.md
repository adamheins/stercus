# Stercus
Stercus is a simple language. Programs are written to operate on a pre-defined
block of memory, similar to brainfuck. The memory block is arbitrarily-sized;
the current compiler used a block of 10,000 bytes.

The memory is random-accessed using __applicators__. Applicators "apply" an
application to a byte of memory. An applicator is denoted by square brackets
([]), and takes the form `[<byte> <applications...>]. There is no limit to the
number of applications applied in a single applicator. Applicators return the
value stored at the memory location which they are acting on. Applicators may
be used without any applications to just return the value at a memory location.

Conditional statements are loops are achieved using round brackets (()). They
take the from `(<applicator> <code...>)`. The program will loop between the
brackets until the value returned by the applicator is equal to zero (similar
to a while loop in other languages). If the value of the applicator is zero
initially, the remaining code between the round brackets will not be run.

__Applications__ act on bytes in the memory. There are a number of built-in
applications, and custom ones can be programmed. Applications are similar to
functions in other languages, except that they take no explicit arguments and
do not explicitly return values. Applications are implicitly passed the location
of the byte in memory on which they are acting.

The built-in functions are:

`<number>`: A number from 0 to 127. Assigns the byte in the memory to the
value of the number. Attempting to use a number outside of 0 to 127 results
in undefined behaviour.

`.`: Output the value stored in this memory location.

`,`: Input a value and store it in this memory location.

`+`: Increment the value stored in this memory location.

`-`: Decrement the value stored in this memory location.

Custom applications are denoted by curly brackets ({}). The application takes
the form `{<name> <application code...>}`. The `<name>` is the name of the
application and must be unique. The application code is just regular stercus
code, acting on the globally-accessible memory. The location of the byte to
which the application is being applied is held in the special `$` variable.
This variable only exists within applications and may not be reassigned.
