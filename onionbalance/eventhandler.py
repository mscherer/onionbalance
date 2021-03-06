# -*- coding: utf-8 -*-
from builtins import str, object

import stem

from onionbalance import log
from onionbalance import descriptor
from onionbalance import consensus

logger = log.get_logger()


class EventHandler(object):

    """
    Handles asynchronous Tor events.
    """

    @staticmethod
    def new_status(status_event):
        """
        Parse Tor status events such as "STATUS_GENERAL"
        """
        # pylint: disable=no-member
        if status_event.status_type == stem.StatusType.GENERAL:
            if status_event.action == "CONSENSUS_ARRIVED":
                # Update the local view of the consensus in OnionBalance
                consensus.refresh_consensus()

    @staticmethod
    def new_desc(desc_event):
        """
        Parse HS_DESC response events
        """
        logger.debug("Received new HS_DESC event: %s", str(desc_event))

    @staticmethod
    def new_desc_content(desc_content_event):
        """
        Parse HS_DESC_CONTENT response events for descriptor content

        Update the HS instance object with the data from the new descriptor.
        """
        logger.debug("Received new HS_DESC_CONTENT event for %s.onion",
                     desc_content_event.address)

        #  Check that the HSDir returned a descriptor that is not empty
        descriptor_text = str(desc_content_event.descriptor).encode('utf-8')

        # HSDir's provide a HS_DESC_CONTENT response with either one or two
        # CRLF lines when they do not have a matching descriptor. Using
        # len() < 5 should ensure all empty HS_DESC_CONTENT events are matched.
        if len(descriptor_text) < 5:
            logger.debug("Empty descriptor received for %s.onion",
                         desc_content_event.address)
            return None

        # Send content to callback function which will process the descriptor
        descriptor.descriptor_received(descriptor_text)

        return None
