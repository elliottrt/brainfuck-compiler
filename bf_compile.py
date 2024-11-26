import os
from typing import TextIO
from types import ModuleType

from bf_types import JumpPair, Program, CodeHeader, CodeFooter, Options, CodeCommand, CodeArguments
import bf_i386
import bf_x86_64
import bf_arm64


def get_jump_pair(i: int, jump_pairs: list[JumpPair]) -> int:
	for pair in jump_pairs:
		if pair[0] == i:
			return pair[1]
		elif pair[1] == i:
			return pair[0]
	assert False, "jump pair not found."


# TODO: stack instead of depth?
def locate_pair(i: int, commands: Program) -> int:
	depth: int = 0
	for cmdi in range(i, len(commands)):
		if commands[cmdi] == '[':
			depth += 1
		if commands[cmdi] == ']':
			depth -= 1
		if depth == 0:
			return cmdi
	assert False, "number of [ and ] do not match"


def gen_jump_pairs(commands: Program) -> list[JumpPair]:
	pairs: list[JumpPair] = []
	for i, cmd in enumerate(commands):
		if cmd == '[':
			pairs.append((i, locate_pair(i, commands)))
	return pairs


def valid_bf_char(c: str) -> bool:
	return c in ['+', '-', '<', '>', '.', ',', '[', ']']


def write_header(f: TextIO, header: CodeHeader, options: Options) -> None:
	for line in header(options):
		if options['asm_comments'] or '//' not in line:
			f.write(line)


def write_footer(f: TextIO, footer: CodeFooter, options: Options) -> None:
	for line in footer(options):
		if options['asm_comments'] or '//' not in line:
			f.write(line)


def write_command(f: TextIO, command: CodeCommand, instr: str, i: int, jump_pairs: list[JumpPair], options: Options) -> None:
	instruction: str = instr[0]
	amount: str = instr[1:]

	args: CodeArguments = []

	if instruction in ['+', '-', '<', '>'] and len(amount) != 0:
		args.append(amount)
	elif instruction in ['[', ']']:
		args.append(str(get_jump_pair(i, jump_pairs)))
		args.append(str(i))

	for line in command(instruction, args, options):
		if options['asm_comments'] or '//' not in line:
			f.write(line)


def run_optimizations(contents: str, optimize: bool) -> Program:
	# ensure valid chars
	contents = "".join([c for c in contents if valid_bf_char(c)])

	commands: Program = []

	if optimize:
		i = 0
		while i < len(contents):
			# [-] and [+] set a cell to 0
			if i < len(contents) - 2 and contents[i] == '[' and contents[i + 1] in ('+', '-') and contents[i + 2] == ']':
				commands.append('0')
				i += 3
			# if there are multiple + in a row, combine them
			elif contents[i] == '+':
				total = 0
				while contents[i] == '+':
					total += 1
					i += 1
				commands.append(f'+{total}')
			# if there are multiple - in a row, combine them
			elif contents[i] == '-':
				total = 0
				while contents[i] == '-':
					total += 1
					i += 1
				commands.append(f'-{total}')
			# if there are multiple < in a row, combine them
			elif contents[i] == '<':
				total = 0
				while contents[i] == '<':
					total += 1
					i += 1
				commands.append(f'<{total}')
			# if there are multiple > in a row, combine them
			elif contents[i] == '>':
				total = 0
				while contents[i] == '>':
					total += 1
					i += 1
				commands.append(f'>{total}')
			# otherwise just add it to the list
			else:
				commands.append(contents[i])
				i += 1
	else:
		for c in contents:
			if c in ['+', '-', '<', '>']:
				commands.append(c + '1')
			else:
				commands.append(c)

	return commands


def compile_bf(options: Options) -> None:

	contents: str = ''
	with open(options['input_file'], 'r') as file:
		contents = file.read()

	commands: Program = run_optimizations(contents, options['optimize'])

	options['write_used'] = commands.count('.') > 0
	options['read_used'] = commands.count(',') > 0

	jump_pairs: list[JumpPair] = gen_jump_pairs(commands)

	asmname: str = options['out'] if options['asm_only'] else f'{options["out"]}.asm'
	oname: str = f'{options["out"]}.o'

	bf_asm: ModuleType = {
		'i386': bf_i386,
		'x86_64': bf_x86_64,
		'arm64': bf_arm64
	}.get(options['asm_target'], bf_x86_64)

	with open(asmname, 'w') as asmfile:
		write_header(asmfile, bf_asm.header, options)
		for (index, cmd) in enumerate(commands):
			write_command(asmfile, bf_asm.command, cmd, index, jump_pairs, options)
		write_footer(asmfile, bf_asm.footer, options)

	if not options['asm_only']:
		os.system(f'as {asmname} -o {oname} -arch {options["asm_target"]} {options["as_args"]}')
		os.system(f'ld {oname} -o {options["out"]} -arch {options["asm_target"]} {options["ld_args"]}')

		os.system(f'rm -f {oname}')
		os.system(f'rm -f {asmname}')
