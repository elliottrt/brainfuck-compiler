#!/usr/bin/python3

from bf_compile import compile_bf
import argparse
import sys

'''
TODO: instead of \n at the end of all bf_<target>.py assembly, append with code
TODO: only change rdi/x1 when we switch from reading to writing
TODO (BUG): ,.,. only reads and writes once -> why?
TODO: figure out if i386 works
TODO: x86 compilation target
TODO (BUG): whey does e.bf cause a bus error?
TODO: make options['asm_comments'] a command line option
TODO: calls to c std library instead of syscalls (option?)
TODO: add simulation mode
TODO: add tests
'''


def get_arg_or_default(ident: str, default: str) -> str:
    i: int = 0
    while i < len(sys.argv):
        if sys.argv[i].startswith((ident, ident.upper())):
            if len(sys.argv[i]) - len(ident) == 0:
                if i + 1 < len(sys.argv):
                    return sys.argv[i + 1]
                else:
                    print(
                        f'error: expected argument following {ident}, got none'
                    )
            else:
                return sys.argv[i][len(ident):]
        i += 1
    return default


def get_arg_exists(ident: str) -> bool:
    return ident in sys.argv or ident.upper() in sys.argv


def create_argparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='bf.py',
        description='brainfuck compiler'
    )

    # Positional, Required Arguments

    parser.add_argument(
        'input_file',
        help='brainfuck file to compile'
    )

    # Options

    parser.add_argument(
        '-o', '--output', default='a.out', type=str,
        help='name of the output file'
    )

    parser.add_argument(
        '-O', '--optimize', action='store_true',
        help='optimize the output file'
    )

    parser.add_argument(
        '-n', '--no-func', action='store_true',
        help='disable use of functions for read/write'
    )

    parser.add_argument(
        '-c', '--cells', default=10000, type=int,
        help='set number of cells'
    )

    parser.add_argument(
        '-s', '--cell-size', default=8, type=int,
        choices=[8, 16, 32, 64],
        help='set cell size'
    )

    parser.add_argument(
        '-a', '--arch', default='x86_64', type=str,
        choices=['i386', 'x86_64', 'arm64'],
        help='set output architecture'
    )

    # TODO: figure out short name for assembly output
    parser.add_argument(
        '-m', '--asm-only', action='store_true',
        help='only output assembly file, will use -o if given'
    )

    return parser


if __name__ == '__main__':

    parser = create_argparser()
    options = parser.parse_args(sys.argv[1:])

    options.size_name = ''
    options.size_prefix = ''
    options.cell_size_bytes = 1
    options.asm_comments = True
    options.as_args = ''
    options.ld_args = ''

    # intentionally empty
    options.as_args = {

    }.get(options.arch, '')

    options.ld_args = {
        'i386': '-static'
    }.get(options.arch, '')

    if options.arch == 'i386' and options.cell_size == 64:
        parser.error('64 bit cells not valid for i386')

    options.size_name = {
        8: 'byte',
        16: 'word',
        32: 'dword',
        64: 'qword'
    }.get(options.cell_size, 'byte')

    options.size_prefix = options.size_name[0]

    # annoying at&t syntax thingy

    if options.arch in ['i386', 'x86_64'] and options.cell_size == 32:
        options.size_prefix = 'l'

    elif options.arch in ['arm64']:
        options.size_prefix = {
            8: 'b',
            16: 'h',
            32: '',
            64: ''
        }.get(options.cell_size, 'byte')

    options.cell_size_bytes = int(options.cell_size / 8)

    compile_bf(options)
