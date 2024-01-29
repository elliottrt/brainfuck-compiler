#!/usr/bin/python3

from bf_compile import compile_bf
import sys

'''
TODO: only change rdi/x1 when we switch from reading to writing
TODO: bfp/e.bf fails in arm64
TODO: ,.,.,. only reads and writes twice -> why?
TODO: output format should be an option (currently macho64)
TODO: figure out if i386 works
TODO: refactor bf_X to return str instead of List[str] -> '...'\n'...' is a single string
TODO: make options['asm_comments'] a command line option
TODO: calls to c std library instead of syscalls (option?)
'''

def usage(filename: str) -> None:
	print()
	print(f'Usage: {filename} <input file> [options]')
	print('\nOptions:')
	print('-o <filepath> (output filepath)')
	print('-no (don\'t optimize output)')
	print('-nrwf (disable subroutines for read and write)')
	print('-cc (set number of cells)')
	print('-cs (cell size in bits - 8, 16, 32, 64)')
	print('-arch (architecture - i386, x86_64, arm64)')
	print('-asm (only output assembly file, will use -o <filename> if specified)')
	print()
	exit(0)

def get_arg_or_default(ident: str, default: str) -> str:
	i = 0
	while i < len(sys.argv):
		if sys.argv[i].startswith((ident, ident.upper())):
			if len(sys.argv[i]) - len(ident) == 0:
				if i + 1 < len(sys.argv):
					return sys.argv[i + 1]
				else:
					print(f'Error: expected argument following {ident}, got none')
			else:
				return sys.argv[i][len(ident):]
		i += 1
	return default

def get_arg_exists(ident: str) -> bool:
	return ident in sys.argv or ident.upper() in sys.argv

if __name__ == '__main__':
	if len(sys.argv) < 2: usage(__file__)

	options = {
		'input_file': sys.argv[1],
		'out': get_arg_or_default('-o', 'out'),
		'optimize': not get_arg_exists('-no'),
		'rwfunc': not get_arg_exists('-nrwf'),
		'cell_count': int(get_arg_or_default('-cc', '10000')),
		'cell_size': int(get_arg_or_default('-cs', '8')),
		'asm_target': get_arg_or_default('-arch', 'x86_64'),
		'size_name': '',
		'size_prefix': '',
		'cell_size_bytes': 1,
		'output_format': 'macho64',
		'asm_comments': False,
		'as_args': '',
		'ld_args': '',
		'asm_only': get_arg_exists('-asm')
	}

	if options['asm_target'] not in ['i386', 'x86_64', 'arm64']:
		print(f'Error: invalid arch {options["asm_target"]}')
		exit(1)

	options['as_args'] = {
		
	}.get(options['asm_target'], '')

	options['ld_args'] = {
		'i386': '-static'
	}.get(options['asm_target'], '')

	if options['cell_size'] not in [8, 16, 32, 64]:
		print(f'Error: invalid cell size {options["cell_size"]}')
		exit(1)

	if options['asm_target'] == 'i386' and options['cell_size'] == 64:
		print(f'Error: 64 bit cells not valid for i386')
		exit(1)

	options['size_name'] = {
		8: 'byte',
		16: 'word',
		32: 'dword',
		64: 'qword'
	}.get(options['cell_size'], 'byte')

	options['size_prefix'] = options['size_name'][0]

	# annoying at&t syntax thingy
	if options['asm_target'] in ['i386', 'x86_64'] and options['cell_size'] == 32:
		options['size_prefix'] = 'l'
	elif options['asm_target'] in ['arm64']:
		options['size_prefix'] = {
			8: 'b',
			16: 'h',
			32: '',
			64: ''
		}.get(options['cell_size'], 'byte')

	options['cell_size_bytes'] = int(options['cell_size'] / 8)

	compile_bf(options)
