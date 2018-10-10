import ipaddress
import argparse
import math
import re
import embededv42V6


class Map_T:
    def __init__(self, ipv6_prefix, ipv4_prefix, psid_offset=6, psid_len=5, ea_len=6):
        self.ipv6_prefix = ipaddress.IPv6Network(ipv6_prefix)
        self.ipv4_prefix = ipaddress.IPv4Network(ipv4_prefix)
        self.psid_offset = psid_offset
        self.psid_len = psid_len
        self.ea_len = ea_len
        if self.ipv4_prefix.is_private:
            try:
                raise ValueError('Invalid ipv4 netmask, %s is not a public ipv4 address'% self.ipv4_prefix)
                raise Exception('Invalid ipv4 netmask, %s is not a public ipv4 address'% self.ipv4_prefix)
            except Exception as error:
                print('Caught this error: ' + repr(error))

    def start_port(self):
        return int(math.pow(2,(16-self.psid_offset)))
    def sharing_ratio(self):
        if self.ea_len + self.ipv4_prefix.prefixlen <=32:
            return "1/" + str(int(math.pow(2, (32-self.ea_len - self.ipv4_prefix.prefixlen))))
        else:
            return str(int(math.pow(2,(self.psid_len)))) + "/1"
    def port_per_user(self):
        if self.ea_len + self.ipv4_prefix.prefixlen <=32:
            return 65535
        else:
            return int(math.pow(2,(16-self.psid_len))- math.pow(2,16-self.psid_len-self.psid_offset))
    def user_num(self):
        return int(math.pow(2, self.ea_len))
    def ipv4_add_num(self):
        return self.ipv4_prefix.num_addresses 
    def summury(self):
        print("IPV4 Prefix: %s"% self.ipv4_prefix)
        print("Total IPV4 address: %d"% self.ipv4_add_num())
        print("Total users: %d"% self.user_num())
        print("Sharing ratio (private:public) : %s"% self.sharing_ratio())
        print("Port per user: %s"% self.port_per_user())
    

class Map_T_CE(Map_T):
    def __init__(self, Map_t, psid):
        self.ipv6_prefix = Map_t.ipv6_prefix
        self.ipv4_prefix = Map_t.ipv4_prefix
        self.psid_offset = Map_t.psid_offset
        self.psid_len = Map_t.psid_len
        self.ea_len = Map_t.ea_len
        self.psid = psid

    def bmr_v4_2_v6(self, ipv4_address):
        ipv4_address = ipaddress.IPv4Address(ipv4_address)
        ea_bits_offset = 128-self.ipv6_prefix.prefixlen-self.ea_len
        ipv4_suffix = int(self.ipv4_prefix.network_address)
        ea_bits = (ipv4_suffix << (self.ea_len+self.ipv4_prefix.prefixlen-32)) | self.psid
        interface_id = int(ipv4_address)<<16 | self.psid
        ipv6_address = int(self.ipv6_prefix.network_address) | interface_id | (ea_bits<<ea_bits_offset)
        ipv6_address = ipaddress.IPv6Address(ipv6_address)
    def dmr_v4_2_v6(self, ipv6_prefix, ipv4_address):
        return embededv42V6.embededv42V6(ipv6_prefix, ipv4_address)
        

class Map_T_BR(Map_T):
    def __init__(self, Map_t):
        self.ipv6_prefix = Map_t.ipv6_prefix
        self.ipv4_prefix = Map_t.ipv4_prefix
        self.psid_offset = Map_t.psid_offset
        self.psid_len = Map_t.psid_len
        self.ea_len = Map_t.ea_len
    
    def dhcp_s46_rule(self):
        OPTION_S46_RULE=89
        flag = 0x0
        ea_len = self.ea_len
        prefix4_len = self.ipv4_prefix.prefixlen
        ipv4_prefix = self.ipv4_prefix.network_address
        prefix6_len = self.ipv6_prefix.prefixlen
        ipv6_prefix = int(self.ipv6_prefix.network_address)
        ipv4_prefix = "{:08X}".format(int(ipv4_prefix))
        ipv6_prefix = "{:X}".format(ipv6_prefix)
        prefix_mask = re.compile("0+$")
        ipv6_prefix = prefix_mask.sub('', ipv6_prefix)
        #right 0 padding
        if(math.ceil(len(ipv6_prefix)/2) -len(ipv6_prefix)/2 > 0.01 ):
            ipv6_prefix+="0"
        length = 8 + int(len(ipv6_prefix)/2)
        return ("{:04X}{:04X}{:02X}{:02X}{:02X}{:s}{:02X}{:s}".format(OPTION_S46_RULE, length, flag, ea_len, prefix4_len, ipv4_prefix, prefix6_len, ipv6_prefix))

    def dhcp_s64_dmr(self, dmr_ipv6_prefix):
        OPTION_S46_DMR = 91
        ipv6_prefix = ipaddress.IPv6Network(dmr_ipv6_prefix)
        prefix6_len = ipv6_prefix.prefixlen
        ipv6_prefix = int(self.ipv6_prefix.network_address)
        ipv6_prefix = "{:X}".format(ipv6_prefix)
        prefix_mask = re.compile("0+$")
        ipv6_prefix = prefix_mask.sub('', ipv6_prefix)
        #right 0 padding
        if(math.ceil(len(ipv6_prefix)/2) -len(ipv6_prefix)/2 > 0.01 ):
            ipv6_prefix+="0"
        length = 1 + int(len(ipv6_prefix)/2)
        return("{:04X}{:04X}{:02X}{:s}").format(OPTION_S46_DMR, length, prefix6_len, ipv6_prefix)
    
    def dhcp_s46_portparams(self, psid):
        OPTION_S46_PORTPARAMS = 93
        length = 4
        return("{:04X}{:04X}{:02X}{:02X}{:04X}").format(OPTION_S46_PORTPARAMS, length, self.psid_offset, self.psid_len, psid)
    def trans_v6_2_v4(self, src_ipv6_address, dst_ipv6_add, src_port):
        print("")
    def trans_v4_2_v6(self, src_ipv6_address, dst_ipv6_add, dst_port):
        print("")
    

"""

map_t_sys = Map_T("2001:db8:ffff:f000::/52", "46.103.1.1/32", 6, 4, 4)

map_t_sys.summury()


map_t_ce = Map_T_CE(map_t_sys, 0x01)
map_t_br = Map_T_BR(map_t_sys)


print (map_t_br.dhcp_s46_rule())
print (map_t_br.dhcp_s64_dmr("2001:db8:0:def::/64"))
print (map_t_br.dhcp_s46_portparams(0x01))

map_t_ce.bmr_v4_2_v6("46.103.1.1")



"""


