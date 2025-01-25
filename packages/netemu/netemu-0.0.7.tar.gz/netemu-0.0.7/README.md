# NetEMU

A lightweight, rootless network emulator for Linux. Written in Python without any dependencies.

## Example

```sh
# python -m netemu
> new 
[469392] Created node n1
> new
[469418] Created node n2
> new switch
[469450] Created switch sw1
> n1 connect sw1
Connected n1 to sw1
> n2 connect sw1
Connected n2 to sw1
> n1 ip a add 10.0.0.1/24 dev veth_sw1
> n2 ip a add 10.0.0.2/24 dev veth_sw1
> n1
sh-5.2# ping 10.0.0.2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.069 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.046 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.041 ms
^C
--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2063ms
rtt min/avg/max/mdev = 0.041/0.052/0.069/0.012 ms
sh-5.2# exit
> exit
```
