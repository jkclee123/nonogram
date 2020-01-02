import time
from board import board

if __name__ == "__main__":
	board = board()
	# board.input_info()
	board.set_info(10, [(2,), (4,), (6, 1), (6, 2), (10,), (5, 1, 2), (7, 2), (5, 1), (4,), (2,)], [(6,), (8,), (10,), (10,), (8,), (3, 1), (3,), (1,), (6,), (4,)])
	start_time = time.time()
	count = board.solve()
	elapsed_time = time.time() - start_time
	board.print_board()
	print("Looped %d times" % (count))
	print("Solved in %.2fs" % (elapsed_time * 100))
