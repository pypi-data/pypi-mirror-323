# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2025 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import unittest
import pytest

from time import sleep
from socketio import Client

from klat_connector.utils.sio_connection_utils import start_socket, SocketIOCompat


class EncryptorTests(unittest.TestCase):
    def test_generate_hash(self):
        from klat_connector.utils.encryptor import generate_hash
        hashed = generate_hash("test123")
        self.assertIsInstance(hashed, list)
        self.assertTrue(all((isinstance(x, int) for x in hashed)))


class HtmlUtilsTests(unittest.TestCase):
    def test_clean_html_entities_valid(self):
        from klat_connector.utils.html_utils import clean_html_entities
        cleaned = clean_html_entities("&quot;hello&quot;")
        self.assertEqual(cleaned, '"hello"')
        cleaned = clean_html_entities("\"hello\"")
        self.assertEqual(cleaned, '"hello"')


class LegacySocketAdapterTests(unittest.TestCase):
    from klat_connector.utils.legacy_socket_adapter import SocketIOCompat
    # TODO


class MachServerTests(unittest.TestCase):
    from klat_connector.utils.mach_server import MachKlatServer
    from klat_connector.klat_api import KlatApi
    from klat_connector.utils.sio_connection_utils import start_socket
    sio_server = MachKlatServer()
    sleep(1)  # Pad to allow mach server to start up
    sio_client = KlatApi(start_socket("0.0.0.0"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sio_server.shutdown_server()
        cls.sio_client.socket.disconnect()

    @pytest.mark.timeout(5)
    def test_mock_users(self):
        conversation_users = self.sio_client.conversation_users
        this_user = self.sio_client.nick
        self.assertEqual(conversation_users, [this_user])

    @pytest.mark.timeout(5)
    def test_mock_login(self):
        self.sio_client.login_klat("testlogin", "")
        self.assertEqual(self.sio_client.conversation_users, ["testlogin"])

    @pytest.mark.timeout(5)
    def test_mock_logout(self):
        self.assertFalse(self.sio_client.nick.startswith("guest"))
        self.sio_client.logout_klat()
        self.assertTrue(self.sio_client.nick.startswith("guest"))
        self.assertEqual(self.sio_client.conversation_users, [self.sio_client.nick])

    @pytest.mark.timeout(5)
    def test_mock_domain(self):
        self.assertEqual(self.sio_client._dom, "klattalk.com")
        klat_cid = self.sio_client._cid
        self.sio_client.change_domain("Private")
        self.assertFalse(self.sio_client.is_current_cid(klat_cid))
        self.sio_client.change_domain("klattalk.com")
        self.assertTrue(self.sio_client.is_current_cid(klat_cid))

    @pytest.mark.timeout(5)
    def test_mock_register(self):
        self.sio_client.register_klat("new_user", "password")
        self.assertEqual(self.sio_client.nick, "new_user")
        self.sio_client.logout_klat()
        self.assertTrue(self.sio_client.nick.startswith("guest"))

    def test_mock_login_to_domain(self):
        from klat_connector.klat_api import KlatApi
        api = KlatApi(start_socket("0.0.0.0"), "chatbotsforum")
        api.login_klat("test_user", "password")
        self.assertEqual(api.nick, "test_user")
        self.assertEqual(api._dom, "chatbotsforum")
        api.socket.disconnect()


class SocketConnectionTests(unittest.TestCase):
    def test_start_socket(self):
        socket = start_socket()
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.disconnect()

    def test_start_socket_bad_port_timeout(self):
        socket = start_socket("2222.us", 80, 3)
        self.assertFalse(socket.connected)

    @pytest.mark.skip("Server is decommissioned")
    def test_2222_socket(self):
        socket = start_socket("2222.us", 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.emit("test event", ["data0", "data1", 2])
        socket.emit("test event", ("data0", "data1", 2))
        socket.disconnect()

    @pytest.mark.skip("Server is decommissioned")
    def test_3333_socket(self):
        socket = start_socket("3333.us", 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.emit("test event", ["data0", "data1", 2])
        socket.emit("test event", ("data0", "data1", 2))
        socket.disconnect()

    @pytest.mark.skip("Server is decommissioned")
    def test_5555_socket(self):
        socket = start_socket("5555.us", 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.emit("test event", ["data0", "data1", 2])
        socket.emit("test event", ("data0", "data1", 2))
        socket.disconnect()

    def test_0000_socket(self):
        socket = start_socket("0000.us", 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.emit("test event", ["data0", "data1", 2])
        socket.emit("test event", ("data0", "data1", 2))
        socket.disconnect()

    @pytest.mark.skip("Server is decommissioned")
    def test_6666_socket(self):
        socket = start_socket("6666.us", 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.emit("test event", ["data0", "data1", 2])
        socket.emit("test event", ("data0", "data1", 2))
        socket.disconnect()


if __name__ == '__main__':
    unittest.main()
