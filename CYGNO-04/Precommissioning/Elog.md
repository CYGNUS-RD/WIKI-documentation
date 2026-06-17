# 17/06/2026 - Setup of network connection at LNF

- DAQ server has two network cards: `Intel Corporation I210 Gigabit Network Connection` (`eno1`) and `Aquantia Corp. AQC107 NBase-T/IEEE 802.3bz Ethernet Controller` (`eno2`) 
- External connection to `eno2` (1 Gbps connection required)
- The `eno1` is used as an interface to a local isolated network with the following connection:

```
    [Server]
      eno1
        |
    [Switch]
    DGS-1005D
      |     |
    ISEG  CAENHV
```

The following procedure has been done:
### Step 1: assign an IP to `eno1`

```
sudo ip addr add 10.50.0.1/24 dev eno1
sudo ip link set eno1 up
```

### Step 2: setup a DHCP server only on eno1

If `dnsmasq` not installed, do:
```
sudo apt install dnsmasq
```

Then create the file `/etc/dnsmasq.d/dispositivi.conf` with the following content:

```
interface=eno1

bind-interfaces

dhcp-range=10.50.0.100,10.50.0.150,255.255.255.0,12h

dhcp-host=00:80:a3:e1:9c:01,10.50.0.110
dhcp-host=00:90:fb:66:2f:2c,10.50.0.115
```
where `00:80:a3:e1:9c:01` is the MAC address of the ISEG and the `00:90:fb:66:2f:2c` is the MAC address of the CAEN HV crate.

Now restart the `DHCP` server:
```
sudo systemctl restart dnsmasq
```

To crosscheck the correct IP assignment do:
```
cat /var/lib/misc/dnsmasq.leases
```

Note: the `10.50.0.114` (MAC address `3c:ec:ef:6c:e2:04`) is the internal remote control interface

