def __substi(src: str, bound: tuple[int, int]=(0, 9), 
			count: int=0) -> str:
	from random import randint
	out = ''
	c = 0
	for i in src:
		if i == 'x':
			if count != 0 and count <= c:
				out += i
				continue

			out += str(randint(*bound))
			c += 1

		else: out += i

	return out.lstrip('0')


def ipv4(fmt: str=None) -> str:
	from random import randint
	if fmt == None:
		M = 2**32 - 1
		X = randint(0, M)
		ipv4arr = []
		for i in range(3, -1, -1):
			ipv4arr.append(str((X >> (8 * i)) % 256))

		return '.'.join(ipv4arr)

	else:
		dat = fmt.lower()
		dat = dat.split('.')
		result = []
		if len(dat) != 4: 
			raise ValueError('not ipv4')

		for d in dat:
			test_x = d.replace('x', '')
			if (not test_x.isnumeric()) and len(test_x) != 0:
				raise ValueError('invalid format')

			if len(d) > 3 or len(d) == 0: 
				raise ValueError('invalid ipv4')
				
			if d.isnumeric():
				int_d = int(d)
				if not (0 <= int_d < 256):
					raise ValueError('invalid ipv4')

				result.append(d)

			else:
				if len(d) == 3:
					if not (d[0] in '012x'):
						raise ValueError('invalid ipv4')

					# This case is about 2x_, 2_x, and 2xx
					# _ is one of any decimals (0-9)
					# ? can be _ or x
					#
					# 2xx
					if d[0] == '2':
						if d[1] == d[2] and d[1] == 'x':
							result.append(f'2{randint(0, 55):02}')
							continue

						# 2x_
						elif d[1] == 'x': 
							if int(d[2]) > 5:
								d = __substi(d, (0, 4))

							else:
								d = __substi(d, (0, 5))

						# 2_x
						else:
							if int(d[1]) > 5:
								raise ValueError('invalid ipv4')

							elif d[1] == '5':
								d = __substi(d, (0, 5))

							else:
								d = __substi(d)

					else: # case: ???
						# xxx
						if d == 'xxx':
							d = str(randint(0, 255))

						# x??
						elif d[0] == 'x': 
							# x_?
							if d[1] != 'x':
								tmp = int(d[1])
								if tmp > 5:
									d = __substi(d, (1, 1), 1)
									d = __substi(d, (0, 9))

								elif tmp == 5:
									if d[2] != 'x':
										tmp = int(d[2])
										if tmp > 5:
											d = __substi(d, (1, 1), 1)
										else:
											d = __substi(d, (1, 2), 1)

									d = __substi(d, (0, 5))

								else:
									d = __substi(d, (1, 2), 1)
									d = __substi(d, (0, 9))

							# xx_
							else:
								if int(d[2]) > 5:
									tmp = str(randint(10, 24))

								else:
									tmp = str(randint(10, 25))
								
								d = tmp + d[2]
								
						# _??
						else: 
							if d[0] != 'x':
								tmp = int(d[0])
								if tmp > 2: 
									raise ValueError('invalid ipv4')
								# 2?? is already haldled
								# therefore thid cases are
								# 1??, and 0??
								d = __substi(d, (0, 9))

					result.append(d)

				# ?, and ??
				else:
					if d[0] == 'x':
						d =__substi(d, (1, 9), 1)

					d = __substi(d, (0, 9))
					result.append(d)

		return '.'.join(result)


def ipv6(fmt: str=None) -> str:
	from random import randint
	M = 2**128 - 1
	X = randint(0, M)
	ipv6arr = []
	for i in range(7, -1, -1):
		ipv6arr.append(hex((X >> (16 * i)) % 65536)[2:])

	return ':'.join(ipv6arr)
