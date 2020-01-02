from itertools import combinations
import functools
from bcolors import bcolors

class board:
	def __init__(self):
		self.size = 0
		self.hint_bitint_dict = dict()

	def input_info(self):
		self.size = int(input("Board size: "))
		self.col_hint_list = self.input_hint_list("col")
		self.row_hint_list = self.input_hint_list("row")

	def set_info(self, size, col_hint_list, row_hint_list):
		self.size = size
		self.col_hint_list = col_hint_list
		self.row_hint_list = row_hint_list

	def input_hint_list(self, name):
		hint_list = list()
		for index in range(self.size):
			hints = input("%s %d: " % (name, index + 1))
			hints_split = [int(hint) for hint in hints.strip().split(" ")]
			hint_list.append(tuple(hints_split))
		return hint_list

	def build_board(self):
		self.build_hint_bitint_dict()
		# get poss bitint from dict according to hint
		self.col_poss_list = [self.hint_bitint_dict[col_hint] for col_hint in self.col_hint_list]
		self.row_poss_list = [self.hint_bitint_dict[row_hint] for row_hint in self.row_hint_list]
		# 1 fully marked and 1 fully crossed bitint for each row (answer)
		self.row_cross_bitint_list = [bit_int(self.size) for _ in range(self.size)]
		self.row_mark_bitint_list = [bit_int(0) for _ in range(self.size)]

	def build_hint_bitint_dict(self):
		hint_list = self.col_hint_list + self.row_hint_list
		sum_set = set(map(sum, hint_list))
		hint_set = set(hint_list)
		full_comb = list(range(self.size))
		for sum_value in range(self.size + 1):
			if sum_value not in sum_set:
				continue
			comb_list = list(combinations(full_comb, sum_value))
			for comb in comb_list:
				bitint = comb_to_bitint(comb)
				hint = bitint_to_hint(bitint, self.size)
				if hint not in hint_set:
					continue
				if hint not in self.hint_bitint_dict:
					self.hint_bitint_dict[hint] = list()
				self.hint_bitint_dict[hint].append(bitint)

	# solve board, returns loop count
	def solve(self):
		self.build_board()
		count = 0
		while not self.is_endgame():
			self.set_poss_common_bit()
			self.remove_not_poss()
			count += 1
		return count

	# get common bit from all possible bitint, set on answer
	def set_poss_common_bit(self):
		for row_index in range(self.size):
			self.row_cross_bitint_list[row_index] &= functools.reduce(lambda x, y: x | y, self.row_poss_list[row_index])
			self.row_mark_bitint_list[row_index] |= functools.reduce(lambda x, y: x & y, self.row_poss_list[row_index])
		for col_index in range(self.size):
			common_mark = functools.reduce(lambda x, y: x & y, self.col_poss_list[col_index])
			common_cross = functools.reduce(lambda x, y: x | y, self.col_poss_list[col_index])
			for row_index in range(self.size):
				self.row_cross_bitint_list[row_index] &= clear_bit(bit_int(self.size), get_bit(common_cross, row_index), col_index)
				self.row_mark_bitint_list[row_index] |= set_bit(bit_int(0), get_bit(common_mark, row_index), col_index)

	# remove not possible bitint using answer
	def remove_not_poss(self):
		for row_index in range(self.size):
			row_mark_bitint = self.row_mark_bitint_list[row_index]
			row_cross_bitint = self.row_cross_bitint_list[row_index]
			self.row_poss_list[row_index] = [poss_bitint for poss_bitint in self.row_poss_list[row_index] if filter_not_poss(row_mark_bitint, row_cross_bitint, poss_bitint)]
		for col_index in range(self.size):
			col_mark_bitint = bit_int(0)
			col_cross_bitint = bit_int(0)
			for row_index in range(self.size):
				col_mark_bitint = set_bit(col_mark_bitint, get_bit(self.row_mark_bitint_list[row_index], col_index), row_index)
				col_cross_bitint = set_bit(col_cross_bitint, get_bit(self.row_cross_bitint_list[row_index], col_index), row_index)
			self.col_poss_list[col_index] = [poss_bitint for poss_bitint in self.col_poss_list[col_index] if filter_not_poss(col_mark_bitint, col_cross_bitint, poss_bitint)]

	# only 1 poss left -> endgame
	def is_endgame(self):
		for index in range(self.size):
			if len(self.col_poss_list[index]) > 1:
				return False
			if len(self.row_poss_list[index]) > 1:
				return False
		return True

	def print_board(self):
		print()
		for row_index in range(self.size):
			row_answer = self.row_poss_list[row_index][0]
			if row_index % 5 == 0 and row_index != 0:
				for _ in range(self.size + self.size // 5 - 1):
					print(f"{bcolors.BOLD}--{bcolors.ENDC}", end="")
				print()
			for col_index in range(self.size):
				answer = get_bit(row_answer, col_index)
				if col_index % 5 == 0 and col_index != 0:
					print(f"{bcolors.BOLD}|{bcolors.ENDC}", end=" ")
				if answer:
					print(f"{bcolors.GREEN}O{bcolors.ENDC}", end=" ")
				else:
					print(f"{bcolors.RED}X{bcolors.ENDC}", end=" ")
			print()
		print()



# filter out poss bitint not match answer
def filter_not_poss(mark_bitint, cross_bitint, poss_bitint):
	return mark_bitint | poss_bitint == poss_bitint and cross_bitint & poss_bitint == poss_bitint

def comb_to_bitint(comb):
	bitint = bit_int(0)
	for bit in comb:
		bitint = set_bit(bitint, 1, bit)
	return bitint

def bitint_to_hint(bitint, size):
	hint_list = list()
	pos = 0
	for bit in range(size):
		if pos == len(hint_list):
			hint_list.append(0)
		if get_bit(bitint, bit):
			hint_list[pos] += 1
		elif hint_list[pos] > 0:
			pos += 1
	return tuple(filter(lambda x: x != 0, hint_list))

# 1 for marked, 0 for cross
def bit_int(bit_value):
	return pow(2, bit_value) - 1

def set_bit(value, bit_value, bit):
	return value | (bit_value << bit)

def clear_bit(value, bit_value, bit):
	bit_value = bit_value * - 1 + 1
	return value & ~(bit_value << bit)

def get_bit(value, bit):
	return value >> bit & 1

def convert_bitint(bitint, size):
	string = ''
	for bit in reversed(range(size)):
		string += str(bitint >> bit & 1)
	return string