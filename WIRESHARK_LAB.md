# Optional Wireshark Practice Lab

A short, authorized learning exercise to observe DNS resolution and the TCP/TLS setup for a website.

## Steps
1. Install Wireshark from its official website.
2. Select your active Wi-Fi or Ethernet interface and start capture.
3. In Command Prompt, run `nslookup example.com`.
4. Open `https://example.com` in your browser.
5. Stop the capture.

## Display filters
- `dns` — DNS packets.
- `tcp.flags.syn == 1` — TCP SYN packets.
- `tcp.flags.syn == 1 && tcp.flags.ack == 1` — SYN-ACK responses.
- `tls` — TLS records.

## Observe
- DNS query name, record type and response addresses.
- TCP three-way handshake: SYN, SYN-ACK, ACK.
- Destination IP and port 443 for HTTPS.
- TLS handshake records. HTTPS application content is encrypted.

## Questions
1. Which DNS record type did the query use?
2. Which IP address did the DNS response return?
3. Did you observe SYN, SYN-ACK and ACK?
4. Which destination port was used for HTTPS?
5. Why can connection metadata be visible while webpage content remains encrypted?

Do not capture other people's traffic or inspect networks without permission.
