
def rop3(op: int, dst, src, pal):
    """
    Perform a ternary raster operation.

    :parma op: The operation identifier.
    :param dst: The destination surface.
    :param src: The source surface.
    :param pal: The palette/brush to use.
    """
    pass


def rop2(op: int, dst, src):
    """
    Perform a binary raster operation.

    :parma op: The operation identifier.
    :param dst: The destination surface.
    :param src: The source surface.
    """
    pass


def rop_slow(code: str, dst, src, pal):
    """
    Slow but generic fallback implementation of raster operations.

    This function implements the RPN-notation described in [MS-RDPEGDI][1]
    with a generic stack machine. It is much slower than having a hardcoded
    and optimized function for a particular operation, but greatly reduces
    the amount of code required.

    [1]: https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpegdi/a9a85075-e796-45eb-b84a-f399324a1109
    """

    stack = []
    for c in code:
        if c == 'D':
            stack.append(dst)
        elif c == 'S':
            stack.append(src)
        elif c == 'P':
            if pal is None:
                raise SyntaxError('Palette is not present.')
            stack.append(pal)
        else:
            lhs = stack.pop()
            rhs = None
            res = lhs  # TODO: Actually perform the operation.

            if c != 'n':
                rhs = stack.pop()

            if c == 'x':  # XOR
                print(f'{lhs} ^ {rhs}')
            elif c == 'n':  # NOT
                print(f'~{lhs}')
            elif c == 'a':  # AND
                print(f'{lhs} & {rhs}')
            elif c == 'o':  # OR
                print(f'{lhs} | {rhs}')

            stack.append(res)
    out = stack.pop()

    assert len(stack) == 0
    return out
