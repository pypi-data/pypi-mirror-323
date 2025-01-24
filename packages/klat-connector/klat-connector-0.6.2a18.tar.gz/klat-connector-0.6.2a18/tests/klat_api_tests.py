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
import sys
import os
from threading import Event

import psutil
import pytest

from multiprocessing import Process
from time import time
from socketio import Client
from mock import Mock
from ovos_utils.log import LOG

# Required for pytest on GitHub
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from klat_connector.utils.sio_connection_utils import start_socket
from klat_connector.klat_api import KlatApi
from klat_connector.utils.legacy_socket_adapter import SocketIOCompat

SERVER = os.environ.get("server") or "2222.us"


class KlatApiTest(KlatApi):
    def __init__(self, *args, **kwargs):
        self.mock_method = kwargs.pop("mock")
        super().__init__(*args, **kwargs)

    def handle_incoming_shout(self, user: str, shout: str, cid: str, dom: str, timestamp: str):
        LOG.info(f"{user}|{shout}|{cid}|{dom}|{timestamp}")
        self.mock_method(shout, user, dom, cid)


@pytest.mark.skip(reason="Klat 1.0 Test server has been decommissioned")
class KlatAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Obfuscate server address for GHA secret filtering
        LOG.info(f"server={'|'.join(list(SERVER))}")
        cls.socket = start_socket(SERVER)
        cls.klat_api = KlatApi(cls.socket, "Private")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.socket.disconnect()

    def setUp(self) -> None:
        if not self.socket.connected:
            LOG.warning("Socket not connected, recreating")
            self.socket = start_socket(SERVER)
            self.klat_api = KlatApi(self.socket, "Private")

    # @pytest.mark.timeout(30)
    # def test_start_socket(self):
    #     socket = start_socket()
    #     self.assertIsInstance(socket, Client)
    #     self.assertTrue(socket.connected)
    #     socket.disconnect()

    def test_start_socket_with_args(self):
        socket = start_socket(SERVER, 8888)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertTrue(socket.connected)
        socket.disconnect()

    def test_start_socket_bad_port_timeout(self):
        socket = start_socket(SERVER, 80, 5)
        self.assertIsInstance(socket, (Client, SocketIOCompat))
        self.assertFalse(socket.connected)

    def test_klat_api_connection_log(self):
        self.assertTrue(self.socket.connected)

        klat = self.klat_api
        klat.change_domain("Private")
        self.assertEqual(klat.logged_in, 1, "Error Connecting as Guest")
        self.assertIsInstance(klat.conversation_users, list, "Users not Populated")
        self.assertIsInstance(klat.nick, str, "Invalid Nick")
        self.assertFalse(klat.conversation_is_proctored, "Invalid Private Proctored conversation")
        self.assertFalse(klat.is_current_cid(""))

        klat.get_conversation_log()
        self.assertIsInstance(klat.chat_log, list, "Chat Log Invalid!")

    def test_klat_login(self):
        klat = self.klat_api
        self.assertTrue(klat.socket.connected)

        klat.login_klat("testrunner", "testpassword")
        self.assertEqual(klat.logged_in, 2, "Error logging in")
        self.assertTrue(klat.socket.connected)
        klat.logout_klat()
        self.assertEqual(klat.logged_in, 1, "Error logging out")
        self.assertTrue(klat.nick.startswith("guest"), "Not a guest after logging out")

        nick = klat.nick
        klat.login_klat("testrunner", "incorrectPassword")
        self.assertEqual(klat.logged_in, 1, "Unknown exception with wrong password")
        self.assertEqual(nick, klat.nick, "Nick error after failed login!")
        klat.logout_klat()

    def test_klat_register(self):
        # TODO: Troubleshoot this with shared socket/api instance DM
        klat = KlatApi(start_socket(SERVER))
        username = f"testrunner{time()}".split(".")[0]
        self.assertTrue(klat.socket.connected)
        self.assertIsNotNone(klat._dom)
        self.assertTrue(klat.nick.startswith("guest"))

        klat.register_klat(username, "testpassword")
        self.assertEqual(klat.logged_in, 2)
        self.assertEqual(klat.nick, username)
        klat.logout_klat()
        self.assertEqual(klat.logged_in, 1, "Error logging out")
        self.assertTrue(klat.nick.startswith("guest"), "Not a guest after logging out")

        nick = klat.nick
        klat.register_klat(username, "testpassword")
        self.assertEqual(klat.logged_in, 1, "Unknown exception with wrong password")
        self.assertEqual(nick, klat.nick, "Nick error after failed login!")
        klat.socket.disconnect()

    def test_change_conversation(self):
        klat = self.klat_api
        klat.change_domain("Private")
        cid = klat._cid
        self.assertEqual(klat._dom, "Private")
        klat.change_conversation("47562", "klattalk.com")
        self.assertEqual(klat._dom, "klattalk.com")
        self.assertEqual(klat._cid, "47562")

        klat.change_conversation(cid, "Private")
        self.assertEqual(klat._cid, cid)

    def test_change_domain(self):
        klat = self.klat_api
        klat.change_domain("CatTalk.com")
        self.assertEqual(klat._dom, "cattalk.com")
        klat.change_domain("private")
        self.assertEqual(klat._dom, "Private")

    def test_create_goto_conversation(self):
        klat = self.klat_api
        klat.change_domain("klattalk.com")
        new_name = f'NewConvoTest {str(time()).split(".")[0]}'
        cid = klat.create_conversation("klattalk.com", new_name, True)
        self.assertIsNotNone(cid)
        self.assertTrue(klat.is_current_cid(cid))

    def test_create_invalid_conversation(self):
        klat = self.klat_api
        klat.change_domain("klattalk.com")
        cid = klat.create_conversation("Private", "NewConvoTest", True)
        self.assertIsNone(cid)

    def test_create_private_conversation(self):
        klat = self.klat_api
        cid = klat.get_private_conversation(["testrunner"])
        self.assertIsNotNone(cid)
        klat.change_conversation(cid, "Private")

        self.assertEqual(klat._dom, "Private")
        self.assertEqual(klat._cid, cid)

    def test_is_current_cid(self):
        klat = self.klat_api
        cid = klat._cid
        is_current = klat.is_current_cid(cid)
        self.assertTrue(is_current)
        isnt_current = klat.is_current_cid("1")
        self.assertFalse(isnt_current)

    def test_conversation_is_proctored(self):
        klat = self.klat_api
        klat.change_domain("Private")
        self.assertFalse(klat.conversation_is_proctored)

    def test_conversation_users(self):
        klat = self.klat_api
        klat.change_domain("Private")
        users = klat.conversation_users
        self.assertEqual(users, [klat.nick], f"cid={klat._cid}|title={klat.title}")
        klat.change_domain("chatbotsforum.org")
        self.assertIsInstance(klat.conversation_users, list)
        self.assertTrue(len(klat.conversation_users) > 0)
        self.assertIn(klat.nick, klat.conversation_users)

    @pytest.mark.timeout(15)
    def test_send_shout(self):
        test_dom = "aatalk.com"
        test_str = "Hello!"
        mock_method = Mock()
        called = Event()
        mock_method.side_effect = lambda: called.set()

        klat_api = KlatApiTest(start_socket(SERVER), test_dom, mock=mock_method)
        self.klat_api.change_domain(test_dom)
        self.klat_api.send_shout(test_str)
        called.wait(10)
        klat_api.socket.disconnect()
        mock_method.assert_called_once()
        mock_method.assert_called_with(test_str, self.klat_api.nick, test_dom, self.klat_api._cid)

    def test_send_shout_disconnected(self):
        klat = KlatApi(start_socket(SERVER), "Private")
        klat.socket.disconnect()
        with pytest.raises(ConnectionError) as e:
            klat._send_shout("No Connection!", klat._dom, klat._cid, klat._cid, None)
            self.assertTrue(str(e).startswith("Socket disconnected skipping sending:"))

    @pytest.mark.timeout(30)
    def test_multi_socket_connections(self):
        def run_test():
            klat = KlatApi(start_socket(SERVER), "Private")
            cid = klat._cid
            self.assertEqual(klat._dom, "Private")
            self.assertEqual(klat.conversation_users, [klat.nick], klat._cid)
            klat.change_domain("Private")
            self.assertEqual(klat._cid, cid)
            self.assertEqual(klat.title.rsplit('-', 1)[0], f"!PRIVATE:{klat.nick}")
            klat.socket.disconnect()
            return

        processes = []
        for i in range(2):
            p = Process(target=run_test)
            p.start()
            processes.append(p)

        success = True
        for p in processes:
            p.join(10)
            if p.is_alive():
                psutil.Process(p.pid).kill()
                success = False
        # self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
