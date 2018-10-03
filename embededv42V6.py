import ipaddress
import argparse
#Implementation of 6052 IPv6 Addressing of IPv4/IPv6 Translators
#
#

parser = argparse.ArgumentParser(description='An IPv4-embedded IPv6 address calculator')
parser.add_argument('-6', dest='v6', metavar='<v6/length>', help='Provide the IPv6 prefix and size. eg. 2001:db8:cafe::/64')
parser.add_argument('-4', dest='v4', metavar='<v4_address>', help='Provide the IPv4 address to embed')
arg = parser.parse_args()


def embededv42V6 (ipv6network, ipv4address):
    ipv6network = ipaddress.IPv6Network(ipv6network)
    ipv4address = ipaddress.IPv4Address(ipv4address)
    ipv6_prefixlen = ipv6network.prefixlen
    if ipv6_prefixlen == 32:
        return ipaddress.IPv6Address(int(ipv6network.network_address) | (int(ipv4address)<<64));
    elif ipv6_prefixlen == 40:
        l24bits = (int(ipv4address)&(0xffffff00))>>8
        r8bits = int(ipv4address)&(0x000000ff)
        return ipaddress.IPv6Address(int(ipv6network.network_address) | l24bits<<64 | r8bits<<48);
    elif ipv6_prefixlen == 48:
        l16bits = (int(ipv4address)&(0xffff0000))>>16
        r16bits = int(ipv4address)&(0x0000ffff)
        return ipaddress.IPv6Address(int(ipv6network.network_address) | l16bits<<64 | r16bits<<40);
    elif ipv6_prefixlen == 56:
        l8bits = (int(ipv4address)&(0xff000000))>>24
        r24bits = int(ipv4address)&(0x00ffffff)
        return ipaddress.IPv6Address(int(ipv6network.network_address) | l8bits<<64 | r24bits<<32);
    elif ipv6_prefixlen == 64:
        return ipaddress.IPv6Address(int(ipv6network.network_address) | (int(ipv4address)<<24));
    elif ipv6_prefixlen == 96:
        return ipaddress.IPv6Address(int(ipv6network.network_address) | (int(ipv4address)));
    else:
        try:
            raise ValueError('Invalid ipv6 netmask, %s is not an supported embededed network mask'% ipv6_prefixlen)
            raise Exception('Invalid ipv6 netmask, %s is not an supported embededed network mask '% ipv6_prefixlen)
        except Exception as error:
            print('Caught this error: ' + repr(error))
            
def main():
    if arg.v4 is None:
        print("Error: Please specify an IPv4 address to map\n")
        parser.print_help()
        exit(1)
    try:
        v4 = ipaddress.IPv4Address(arg.v4)
    except:
        print("Error: Invalid IPv4 address: %s" % arg.v4)
        exit(1)
    if arg.v6 is None:
        v6 = ipaddress.IPv6Network('64:ff9b::/96')
    else:
        try:
            v6 = ipaddress.IPv6Network(arg.v6)
        except:
            print("Error: Invalid IPv6 prefix: %s" % arg.v6)
            exit(1)
    print (embededv42V6 (v6,v4))


if __name__ == '__main__':
    main()