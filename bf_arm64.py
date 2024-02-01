from bf_types import *

def read_code(options: Options) -> CodeSegment:
    return [
        '\t// read syscall\n',
        '\tmov x0, #0\n',
        '\tmov x1, x3\n',
        # '\tmov x2, #1\n',
        '\tmov x16, #3\n',
        '\tsvc #0\n'
    ]

def write_code(options: Options) -> CodeSegment:
    return [
        '\t// write syscall\n',
        '\tmov x0, #1\n',
        '\tmov x1, x3\n',
        # '\tmov x2, #1\n',
        '\tmov x16, #4\n',
        '\tsvc #0\n'
    ]

def header(options: Options) -> CodeSegment:
    return [
        '.global _main\n',
        '.align 8\n\n',
        '_main:\n',
	    '\t// initialize the cell pointer\n',
	    '\tadrp x3, cells@PAGE\n',
        '\tadd x3, x3, cells@PAGEOFF\n',
        '\tmov x2, #1\n',
	    '\n// Program Code:\n'
    ]

def footer(options: Options) -> CodeSegment:
    result = [
        '\n// End Program Code\n',
	    '\n\t// exit syscall\n',
	    '\tmov x0, #0\n',
	    '\tmov x16, #1\n',
	    '\tsvc #0\n'
    ]
    if options['rwfunc']:
        if options['read_used']: result.extend(read_func(options))
        if options['write_used']: result.extend(write_func(options))
    result.extend([
        '\n// cell memory reservation\n',
        '.data\n',
        '.align 8\n',
        'cells:\n',
	    f'\t.zero {options["cell_count"] * options["cell_size"] // 8}\n'
    ])
    return result

def command(code: str, args: List[str], options: Options) -> CodeSegment:
    reg_prefix: str = 'x' if options['cell_size'] == 64 else 'w'
    if code == '+':
        return [
            f'\t// add {args[0]}\n',
            f'\tldr{options["size_prefix"]} {reg_prefix}0, [x3]\n',
            f'\tadd {reg_prefix}0, {reg_prefix}0, #{args[0]}\n',
            f'\tstr{options["size_prefix"]} {reg_prefix}0, [x3]\n'
        ]
    if code == '-':
        return [
            f'\t// subtract {args[0]}\n',
            f'\tldr{options["size_prefix"]} {reg_prefix}0, [x3]\n',
            f'\tsub {reg_prefix}0, {reg_prefix}0, #{args[0]}\n',
            f'\tstr{options["size_prefix"]} {reg_prefix}0, [x3]\n'
        ]
    if code == '<':
        return [
            f'\t// move left {args[0]}\n',
            f'\tsub x3, x3, #{int(args[0]) * options["cell_size"] // 8}\n'
        ]
    if code == '>':
        return [
            f'\t// move right {args[0]}\n',
            f'\tadd x3, x3, #{int(args[0]) * options["cell_size"] // 8}\n'
        ]
    if code == '.':
        return [
            '\t// write function call\n',
            '\tbl write\n',
        ] if options['rwfunc'] else write_code(options)
    if code == ',':
        return [
            '\t// read function call\n',
            '\tbl read\n',
        ] if options['rwfunc'] else read_code(options)
    if code == '[':
        return [
            '\t// start of loop\n',
            f'\tldr{options["size_prefix"]} {reg_prefix}0, [x3]\n',
		    f'\tcmp {reg_prefix}0, #0\n',
		    f'\tbeq jump_{args[0]}\n',
		    f'jump_{args[1]}:\n'
        ]
    if code == ']':
        return [
            '\t// end of loop\n',
            f'\tldr{options["size_prefix"]} {reg_prefix}0, [x3]\n',
            f'\tcmp {reg_prefix}0, #0\n',
		    f'\tbne jump_{args[0]}\n',
		    f'jump_{args[1]}:\n'
        ]
    if code == '0':
        return [
            '\t// optimization - zero cell\n',
            f'\tmov {reg_prefix}0, #0\n',
            f'\tstr{options["size_prefix"]} {reg_prefix}0, [x3]\n'
        ]
    assert False, 'unreachable - bf_arm64::command'

def read_func(options: Options) -> CodeSegment:
    result = []
    result.extend([
        'read:\n'
    ])
    result.extend(
        read_code(options)
    )
    result.extend([
        '\tret\n'
    ])
    return result

def write_func(options: Options) -> CodeSegment:
    result = []
    result.extend([
        'write:\n'
    ])
    result.extend(
        write_code(options)
    )
    result.extend([
        '\tret\n'
    ])
    return result
