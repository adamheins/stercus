#!/usr/bin/env python
""" Stercus Language Compiler """

import argparse
import json
from textwrap import dedent

from .constants import *
from .errors import *


def c_header(memory_size):
    return dedent(
        f"""
    #include <stdio.h>
    #include <stdlib.h>

    const size_t {C_DATA_ARRAY_SIZE_NAME} = {memory_size};
    char *{C_DATA_ARRAY_NAME};

    int {C_GET_BYTE_NAME}(int i) {{
        if (i < {C_DATA_ARRAY_SIZE_NAME}) {{
            return {C_DATA_ARRAY_NAME}[i];
        }} else {{
            fprintf(stderr, "attempted out of bounds access to index %d\\n", i);
            return 0;
        }}
    }}

    int {C_SET_BYTE_NAME}(int i, char value) {{
        if (i < {C_DATA_ARRAY_SIZE_NAME}) {{
            {C_DATA_ARRAY_NAME}[i] = value;
        }} else {{
            fprintf(stderr, "attempted out of bounds access to index %d\\n", i);
            return 0;
        }}
    }}

    // copy the CLI args into the main data array
    void _stercus_copy_cli_args(int argc, char* argv[], int max_bytes) {{
      int d_idx = 0;
      for (int c = 1; c < argc; ++c) {{
        int arg_idx = 0;
        while (argv[c][arg_idx]) {{
          {C_DATA_ARRAY_NAME}[d_idx] = argv[c][arg_idx];
          ++arg_idx;
          ++d_idx;
        }}
        if (d_idx >= max_bytes) {{ return; }}

        // add space between args
        if (c < argc - 1) {{
            {C_DATA_ARRAY_NAME}[d_idx] = ' ';
          ++d_idx;
        }}
        if (d_idx >= max_bytes) {{ return; }}
      }}
    }}
    """
    ).strip()


def apply(output, application, accessor, func_list):
    """Apply an application to the accessed location."""
    ele = f"{C_DATA_ARRAY_NAME}[{accessor}]"
    if application == NOP:
        pass
    elif application == INCREMENT:
        # output.append(ele + "++;")
        output.append(
            f"{C_SET_BYTE_NAME}({accessor}, {C_GET_BYTE_NAME}({accessor}) + 1);"
        )
    elif application == DECREMENT:
        # output.append(ele + "--;")
        output.append(
            f"{C_SET_BYTE_NAME}({accessor}, {C_GET_BYTE_NAME}({accessor}) - 1);"
        )
    elif application == OUTPUT_INT:
        output.append(f'printf("%d", {C_GET_BYTE_NAME}({accessor}));')
    elif application == OUTPUT_CHAR:
        output.append(f"putchar({C_GET_BYTE_NAME}({accessor}));")
    elif application == INPUT:
        output.append(f"{C_SET_BYTE_NAME}({accessor}, getchar());")
    elif application in func_list:
        output.append(f"{application}({accessor});")
    else:
        output.append(f"{C_SET_BYTE_NAME}({accessor}, {application});")


def compile_body(tokens, func_list, memory_size=None):
    output = []
    stack = []
    for token in tokens:
        if token == APPLICATOR["CLOSE"]:
            li = []
            val = stack.pop()
            while val != APPLICATOR["OPEN"]:
                li.append(val)
                val = stack.pop()
            li.reverse()

            accessor = li[0]

            # compile-time bounds checking
            if memory_size is not None:
                try:
                    idx = int(accessor)
                    if idx >= memory_size:
                        raise IndexOutOfRangeError(
                            f"attempted out of bounds access to index {idx}; aborting"
                        )
                except ValueError:
                    pass

            for application in li[1:]:
                apply(output, application, accessor, func_list)
            if len(stack) > 0 and stack[-1] == CONDITIONAL["OPEN"]:
                output.append(
                    f"if(!{C_GET_BYTE_NAME}({C_GET_BYTE_NAME}({accessor}))){{break;}}"
                )
            stack.append(f"{C_GET_BYTE_NAME}({accessor})")
        elif token == CONDITIONAL["CLOSE"]:
            val = stack.pop()
            while val != CONDITIONAL["OPEN"]:
                val = stack.pop()
            output.append("}")
        elif token == CONDITIONAL["OPEN"]:
            output.append("while(1){")
            stack.append(token)
        elif token == APPLICATOR["OPEN"]:
            stack.append(token)
        else:
            # Check if the token is the accessor for a conditional.
            if len(stack) > 0 and stack[-1] == CONDITIONAL["OPEN"]:
                output.append(f"if(!{C_GET_BYTE_NAME}({token})){{break;}}")
            stack.append(token)
    return "\n".join(output)


def compile_application(name, tokens, app_list, memory_size):
    """Compile a function from stercus to C."""
    declaration = f"void {name}(char {C_FUNC_ARG_NAME})"
    body = compile_body(tokens, app_list, memory_size)
    definition = f"{declaration} {{\n{body}}}\n"
    return f"{declaration};\n", definition


def compile_main(tokens, app_table, memory_size, argv_max_bytes=None):
    """Compile the main C function."""
    if argv_max_bytes is None:
        argv_max_bytes = C_DATA_ARRAY_SIZE_NAME

    body = compile_body(tokens, app_table, memory_size)
    output = f"""
    int main(int argc, char* argv[]) {{
      {C_DATA_ARRAY_NAME} = (char *)calloc({C_DATA_ARRAY_SIZE_NAME}, sizeof(char));
      _stercus_copy_cli_args(argc, argv, {argv_max_bytes});
      {body}
      free({C_DATA_ARRAY_NAME});
      return 0;
    }}
    """
    return dedent(output).strip()


def compile(applications, memory_size, argv_max_bytes=None):
    """Compile the Stercus function table to C."""

    # Save and remove the main function, as it must be placed at the end of the
    # generated C code.
    main_appl = applications["main"]
    applications.pop("main")

    app_declarations = []
    app_bodies = []

    # Compile applications into C functions.
    for name, content in applications.items():
        body, declaration = compile_application(
            name, content, applications.keys(), memory_size
        )
        app_bodies.append(body)
        app_declarations.append(declaration)

    c_src = c_header(memory_size)
    c_src += "\n".join(app_bodies)
    c_src += "\n".join(app_declarations)

    # Compile the main function.
    c_src += "\n\n" + compile_main(
        main_appl,
        applications.keys(),
        memory_size,
        argv_max_bytes=argv_max_bytes,
    )
    return c_src


def main():
    """Run the compiler as an independent program."""
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Stercus source file.")
    parser.add_argument(
        "-o", "--output", help="Output file for compiled" " result.", dest="out"
    )
    args = parser.parse_args()

    # Tokens are read from a whitespace-separated list in a file.
    with open(args.src, "r") as f:
        applications = json.load(f)

    # Output the result.
    c_src = compile(applications)
    if args.out:
        with open(args.out, "w") as f:
            f.write(c_src)
    else:
        print(c_src)


if __name__ == "__main__":
    main()
