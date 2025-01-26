from randip.gen import ipv4, ipv6

HELP = """\
Usage: randip [ipv4|ipv6] [IP Template]
IP Type
	ipv4, ip4, 4: IPv4 (default)
	ipv6, ip6, 6: IPv6
IP Template(IPv4 only)
	Replace wildcards "X" with proper random digits.
	If a section is "XXX", it can be 0~255.
	A section that has only wildcards(X, XX),
	it will match the digit length.
"""

def main():
	from sys import argv
	action = ''
	if len(argv) < 2:
		action = 'ipv4'

	else: action = argv[1]
	if action in 'ipv4 4 ip4'.split(' '):
		print(ipv4(*argv[2:]))

	elif action in 'ipv6 6 ip6'.split(' '): 
		print(ipv6(*argv[2:]))

	else: 
		print(HELP, end='')

if __name__ == '__main__':
	main()
