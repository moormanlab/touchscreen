For UMass Amherst eduroam networks the following information is needed instead in the `wpa_supplicant.conf` file

```
network={
    ssid="eduroam"
    proto=RSN
    key_mgmt=WPA-EAP
    pairwise=CCMP
    auth_alg=OPEN
    eap=TTLS
    identity="YOUR_NET_ID"
    password="YOUR_NET_PASSWORD"
    phase1="tls_disable_tlsv1_1=1 tls_disable_tlsv1_2=1"
    phase2="auth=PAP"
}
```

Where `YOUR_NET_ID` is the eduroam Net Id: `username@umass.edu` and `YOUR_NET_PASSWORD` is the password.


Also, in the `rootfs` partition edit the file `lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant` (it might require admin priviliges)
(only if wifi is WPA-EAP)
change line 60 from 
```
  wpa_supplicant_driver="${wpa_supplicant_driver:-nl80211,wext}"
```
to
```
  wpa_supplicant_driver="${wpa_supplicant_driver:-wext,nl80211}"
```
