import unittest
from unittest.mock import patch
import netdiag


class NetDiagTests(unittest.TestCase):
    @patch("netdiag.socket.getaddrinfo")
    def test_dns_deduplicates_addresses(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("192.0.2.10", 0)),
            (2, 1, 6, "", ("192.0.2.10", 0)),
            (10, 1, 6, "", ("2001:db8::10", 0, 0, 0)),
        ]
        result = netdiag.dns_lookup("lab.example")
        self.assertTrue(result["success"])
        self.assertEqual(result["addresses"], ["192.0.2.10", "2001:db8::10"])

    @patch("netdiag.socket.create_connection")
    def test_tcp_failure_is_reported(self, mock_connect):
        mock_connect.side_effect = OSError("connection refused")
        result = netdiag.tcp_port("127.0.0.1", 65534)
        self.assertFalse(result["success"])
        self.assertIn("connection refused", result["error"])


if __name__ == "__main__":
    unittest.main()
