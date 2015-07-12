#!/usr/bin/env python

def run(tokens):
    def apply(application, accessor):
        if application == NOP:
            pass
        elif application == INCREMENT:
            data[accessor] += 1
        elif application == DECREMENT:
            data[accessor] -= 1
        elif application == OUTPUT:
            print data[accessor]
        elif application == INPUT:
            data[accessor] = ord(sys.stdin.read(1))
        else:
            data[accessor] = int(application)

    def push(token, index):
        try:
            value = int(token)
            if len(stack) > 0 and data[value] == 0 and stack[-1] == CONDITIONAL_START:
                stack.pop()
                while tokens[index] != CONDITIONAL_END:
                    index += 1
            else:
                stack.append(token)
        except:
            stack.append(token)
        return index

    # The memory we are working with.
    data = [0] * (DATA_SIZE + 1)

    stack = []
    loop_index_stack = []

    index = 0
    while (index < len(tokens)):
        token = tokens[index]
        if token == APPLICATOR_END:
            li = []
            val = stack.pop()
            while val != APPLICATOR_START:
                li.append(val)
                val = stack.pop()
            li.reverse()
            accessor = int(li[0])
            for application in li[1:]:
                apply(application, accessor)
            index = push(accessor, index)
        elif token == CONDITIONAL_END:
            li = []
            val = stack.pop()
            while (val != CONDITIONAL_START):
                li.append(val)
                val = stack.pop()
            accessor = int(li[-1])
            if data[accessor] != 0:
                index = loop_index_stack.pop()
                continue
        elif token == CONDITIONAL_START:
            loop_index_stack.append(index)
            stack.append(token)
        else:
            index = push(token, index)
        index += 1
