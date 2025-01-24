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

import time

from neon_mq_connector.utils.rabbit_utils import create_mq_callback
from pika.exchange_type import ExchangeType

from klat_connector.klat_api_abc import KlatApiABC
from neon_utils import LOG
from neon_mq_connector import MQConnector


class KlatAPIMQ(KlatApiABC, MQConnector):

    def __init__(self, config: dict, service_name: str, vhost: str):
        MQConnector.__init__(self, config, service_name)
        self.current_conversations = set()
        self.vhost = vhost
        self.is_running = False

    @property
    def connected(self) -> bool:
        return self.is_running

    @property
    def nick(self) -> str:
        return self.service_name + '-' + self.service_id

    def handle_incoming_shout(self, message_data: dict):
        """Handles incoming shout for this user"""
        LOG.info(f'Received message data: {message_data}')

    @create_mq_callback()
    def _on_user_message(self, body: dict):
        if body.get('cid', None) in self.current_conversations and (body.get('is_broadcast', False)
                                                                    or body.get('receiver', None) == self.nick):
            self.handle_incoming_shout(body)

    def _send_shout(self, queue_name: str = '', message_body: dict = None, exchange: str = '',
                    exchange_type: str = ExchangeType.direct.value) -> str:
        """
            Sends shout from current instance

            :param queue_name: MQ queue name for emit (optional for publish=True)
            :param message_body: dict with relevant message data
            :param exchange: MQ exchange name for emit
            :param exchange_type: type of exchange to use based on ExchangeType (direct, fanout, topic...)

            :returns generated shout id
        """
        return self.send_message(request_data=message_body,
                                 exchange=exchange,
                                 queue=queue_name,
                                 exchange_type=exchange_type,
                                 expiration=3000)

    def _start_connection(self):
        self.run_consumers()
        self._on_connect()

    def _stop_connection(self):
        self.stop_consumers()
        self._on_disconnect()

    def _on_connect(self):
        self._send_shout('connection', {'nick': self.nick,
                                        'service_name': self.service_name,
                                        'time': time.time()}, publish=True)
        self.is_running = True

    def _on_disconnect(self):
        self._send_shout('disconnection', {'nick': self.nick,
                                           'service_name': self.service_name,
                                           'time': time.time()}, publish=True)
        self.is_running = False

    def _on_reconnect(self):
        self._stop_connection()
        self._start_connection()

    def _setup_listeners(self):
        self.register_consumer('incoming message', self.vhost, 'user_message', self._on_user_message,
                               self.default_error_handler)
