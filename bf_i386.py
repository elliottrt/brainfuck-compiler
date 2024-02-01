from bf_types import *

def read_code(options: Options) -> CodeSegment:
    return [
        '\t//read syscall\n',
        '\tmov $0x02000003, %eax\n',
        '\tmov $0, %edi\n',
        '\tmov $1, %edx\n',
        '\tsyscall\n'
    ]

def write_code(options: Options) -> CodeSegment:
    return [
        '\t// write syscall\n',
        '\tmov $0x02000004, %eax\n',
        '\tmov $1, %edi\n',
        '\tmov $1, %edx\n',
        '\tsyscall\n'
    ]

def header(options: Options) -> CodeSegment:
    return [
        '.text\n\n',
	    '.globl start\n\n',
	    'start:\n',
	    '\t// initialize the cell pointer\n',
	    '\tlea cells, %esi\n',
	    '\n// Program Code:\n'
    ]

def footer(options: Options) -> CodeSegment:
    result = [
        '\n// End Program Code\n',
	    '\n\t// exit syscall\n',
	    '\tmov $0x02000001, %eax\n',
	    '\txor %edi, %edi\n',
	    '\tsyscall\n'
    ]
    if options['rwfunc']:
        if options['read_used']: result.extend(read_func(options))
        if options['write_used']: result.extend(write_func(options))
    result.extend([
        '// cell memory reservation\n',
	    f'.comm cells, {options["cell_count"] * options["cell_size_bytes"]}\n'
    ])
    return result

def command(code: str, args: CodeArguments, options: Options) -> CodeSegment:
    if code == '+':
        if args[0] == '1':
            return [
                f'\t// add 1\n',
                f'\tinc{options["size_prefix"]} (%esi)\n'
            ]
        else:
            return [
                f'\t// add {args[0]}\n',
                f'\tadd{options["size_prefix"]} ${args[0]}, (%esi)\n'
            ]
    if code == '-':
        if args[0] == '1':
            return [
                '\t// subtract 1\n',
                f'\tdec{options["size_prefix"]} (%esi)\n'
            ]
        else:
            return [
                f'\t// subtract {args[0]}\n',
                f'\tsub{options["size_prefix"]} ${args[0]}, (%esi)\n'
            ]
    if code == '<':
        return [
            f'\t// move left {args[0]}\n',
            f'\tsub ${int(args[0]) * options["cell_size_bytes"]}, %esi\n'
        ]
    if code == '>':
        return [
            f'\t// move right {args[0]}\n',
            f'\tadd ${int(args[0]) * options["cell_size_bytes"]}, %esi\n'
        ]
    if code == '.':
        return [
            '\t// write function call\n',
            '\tcall write\n'
        ] if options['rwfunc'] else write_code(options)
    if code == ',':
        return [
            '\t// read function call\n',
            '\tcall read\n'
        ] if options['rwfunc'] else read_code(options)
    if code == '[':
        return [
            '\t// start of loop\n',
		    f'\tcmp{options["size_prefix"]} $0, (%esi)\n',
		    f'\tje jump_{args[0]}\n',
		    f'jump_{args[1]}:\n'
        ]
    if code == ']':
        return [
            '\t// end of loop\n',
            f'\tcmp{options["size_prefix"]} $0, (%esi)\n',
		    f'\tjne jump_{args[0]}\n',
		    f'jump_{args[1]}:\n'
        ]
    if code == '0':
        return [
            '\t// optimization - zero cell\n',
            f'\tmov{options["size_prefix"]} $0, (%esi)\n'
        ]
    assert False, 'unreachable - bf_i386::command'

def read_func(options: Options) -> CodeSegment:
    result = []
    result.extend([
        '\nread:\n',
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
        '\nwrite:\n',
    ])
    result.extend(
        write_code(options)
    )
    result.extend([
        '\tret\n\n'
    ])
    return result
