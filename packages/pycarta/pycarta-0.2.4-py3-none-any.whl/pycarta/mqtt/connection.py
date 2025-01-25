import os
import logging
import time
import threading
from typing import Any, Optional
from uuid import uuid4
from paho.mqtt import client as pclient
from pydantic import BaseModel, Field
from .credential import BaseMqttAuthenticator

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("DEBUG_LEVEL", logging.INFO))

class MQTTConnection:
    """
    Base class for managing MQTT connections with connection, disconnection, and reconnection support.
    """
    POLLING_INTERVAL = float(os.getenv("POLLING_INTERVAL", 0.1))
    POLLING_TIMEOUT = float(os.getenv("POLLING_TIMEOUT", 30))
    CONNECTION_TIMEOUT = float(os.getenv("CONNECTION_TIMEOUT", 5))
    FIRST_RECONNECT_DELAY = int(os.environ.get("FIRST_RECONNECT_DELAY", 1))
    RECONNECT_RATE = int(os.environ.get("RECONNECT_RATE", 2))
    MAX_RECONNECT_COUNT = int(os.environ.get("MAX_RECONNECT_COUNT", 12))
    MAX_RECONNECT_DELAY = int(os.environ.get("MAX_RECONNECT_DELAY", 60))

    class ConnectInfo(BaseModel):
        """Connection information model."""
        userdata: Any
        flags: Any
        return_code: Any
        properties: Any

    def __init__(self,
                 topic: str,
                 *,
                 host: str = "localhost",
                 port: int = 1883,
                 authenticator: BaseMqttAuthenticator | None = None):
        """
        Initialize MQTTConnection.

        Args:
            topic (str): MQTT topic.
            host (str): Broker host. Default is 'localhost'.
            port (int): Broker port. Default is 1883.
            authenticator (BaseMqttAuthenticator): 
                An optional authenticator that configures TLS credentials. Default is None.
        """
        self.topic = topic
        self.host = host
        self.port = port
        self.connect_info = None
        self.authenticator = authenticator
        self.connected_event = threading.Event()

        if self.authenticator is not None:
            # Store the authenticator, create paho client from it
            self.client = authenticator.client(
                callback_api_version=pclient.CallbackAPIVersion.VERSION2,
                client_id=str(uuid4())
            )
        else:
            # Fallback: use the default paho Client (existing behavior)
            self.client = pclient.Client(
                callback_api_version=pclient.CallbackAPIVersion.VERSION2,
                client_id=str(uuid4())
            )

    def __del__(self):
        """Ensure disconnection on object deletion."""
        self.disconnect()

    def connect(self):
        """
        Connect to the MQTT broker.

        This implementation ensures the connection is established before proceeding.
        """
        self.connect_info = None
        self.client.on_connect = self._on_connect
        self.connected_event.clear()

        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")
            self.client.connect(self.host, self.port)
            # loop_start() must be called here to ensure the event loop runs, enabling _on_connect to complete the handshake. Delaying loop_start() would prevent the handshake and cause a timeout.
            self.client.loop_start()

            # CONNECTION_TIMEOUT sets a time limit for the broker to complete the MQTT handshake. loop_start() initiates the event loop in a background thread, and _on_connect is triggered upon success. If the connected_event isn't set within the timeout, the connection attempt is considered failed.
            if not self.connected_event.wait(timeout=self.CONNECTION_TIMEOUT):
                raise ConnectionErrorException(
                    self.host, self.port,
                    f"Connection timed out after {self.CONNECTION_TIMEOUT} seconds. "
                    f"Possible reasons: incorrect broker address, invalid credentials, or network issues."
                )
        except ConnectionErrorException:
            raise  # Directly raise the exception to be handled by the caller
        except Exception as e:
            raise ConnectionErrorException(
                self.host, self.port,
                f"Unexpected error while connecting: {e}. "
                f"Possible reasons: incorrect broker address, invalid credentials, or network issues."
            ) from e


    def reconnect(self):
        """Reconnect to the MQTT broker."""
        self.disconnect()
        self.connect()

    def disconnect(self, client=None, userdata=None, rc=None, properties=None) -> None:
        """
        Disconnect from the MQTT broker or handle disconnection callback.
        """
        if rc is not None:
            logger.info(f"Disconnected with return code {rc}.")
            if rc != 0:
                logger.warning("[MQTTConnection] Unexpected disconnection. Attempting to reconnect...")
                reconnect_successful = self._attempt_reconnect(client, userdata, rc, properties)
                
                if reconnect_successful:
                    logger.info("[MQTTConnection] Reconnection successful. Keeping the loop running.")
                    return

                logger.error("[MQTTConnection] Reconnection failed. Stopping the loop.")
            else:
                self.connect_info = None
        else:
            if self.client.is_connected():
                logger.info("[MQTTConnection] Explicitly disconnecting from broker.")
                self.client.disconnect()
                self.connect_info = None

        logger.info("[MQTTConnection] Stopping the MQTT loop.")
        self.client.loop_stop()


    def _on_connect(self, client, userdata, flags, rc, properties) -> None:
        """Handle successful connection."""
        self.connect_info = self.ConnectInfo(
            userdata=userdata,
            flags=flags,
            return_code=rc,
            properties=properties
        )

        if rc == 0:
            logger.info(f"[MQTTConnection] Connected {userdata} to {self.host}:{self.port}")
            self.connected_event.set()
        else:
            logger.error(f"[MQTTConnection] Failed to connect to {self.host}:{self.port}, return code={rc}")

    def _attempt_reconnect(self, client, userdata, rc, properties) -> bool:
        """
        Attempt to reconnect to the broker. Returns True if successful, False otherwise.
        """
        cls = type(self)
        logger.info(f"Disconnected with return code {rc}.")
        reconnect_count, reconnect_delay = 0, cls.FIRST_RECONNECT_DELAY

        # Reconnection logic uses exponential backoff to manage delays between attempts. Unlike the initial connection timeout, reconnection allows for multiple retries with increasing delays (up to MAX_RECONNECT_DELAY) to handle transient network issues or broker unavailability.
        while reconnect_count < cls.MAX_RECONNECT_COUNT:
            logger.info(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)
            try:
                self.client.reconnect()
                logger.info("Reconnect successful.")
                return True
            except Exception as err:
                logger.error(f"Reconnect failed: {err}")

            reconnect_delay = min(reconnect_delay * cls.RECONNECT_RATE, cls.MAX_RECONNECT_DELAY)
            reconnect_count += 1

        logger.info(f"Reconnect failed after {reconnect_count} attempts.")
        return False

class PubSubStopIteration(StopIteration, StopAsyncIteration):
    """
    Raised to signal the termination of synchronous or asynchronous loops.

    This exception is a specialized form of `StopIteration` and `StopAsyncIteration`, designed for use in MQTT publish/subscribe workflows. It is raised when an MQTT subscription loop needs to terminate gracefully, either due to the completion of a task or a controlled shutdown of the process.

    Attributes:
        message (str): An optional description of the reason for loop termination.
    """

    def __init__(self, message="The publish/subscribe loop has been stopped."):
        super().__init__(message)


class SerializationError(Exception):
    """
    Raised when message serialization fails during MQTT operations.

    This exception indicates that an attempt to serialize a message (e.g., to JSON or another format) has failed. It commonly occurs when the message contains unsupported data types, invalid structures, or other issues incompatible with the serialization format.

    Attributes:
        message (str): A detailed description of the serialization error.
    """

    def __init__(self, message="Message serialization failed."):
        super().__init__(message)


class PublishError(Exception):
    """
    Raised when publishing to the MQTT broker fails.

    This exception indicates that an attempt to publish a message to an MQTT broker was unsuccessful. Common reasons include network issues, broker unavailability, authentication failures, or payload-related problems.

    Attributes:
        message (str): A detailed description of the publishing error.
        topic (str): The topic to which the message was being published.
    """

    def __init__(self, message="Publishing to the MQTT broker failed.", topic=None):
        self.topic = topic
        if topic:
            message += f" (Topic: {topic})"
        super().__init__(message)


class SubscribeError(Exception):
    """
    Raised when subscribing to an MQTT topic fails.

    This exception signals that an attempt to subscribe to an MQTT topic was unsuccessful. Causes can include invalid topic names, lack of permissions, network issues, or broker errors.

    Attributes:
        message (str): A detailed description of the subscription error.
        topic (str): The topic to which the subscription was attempted.
    """

    def __init__(self, message="Subscribing to the MQTT topic failed.", topic=None):
        self.topic = topic
        if topic:
            message += f" (Topic: {topic})"
        super().__init__(message)


class TimeoutException(Exception):
    """
    Raised when an MQTT operation exceeds the allowed time limit.

    This exception is triggered when an operation, such as connecting to the broker, subscribing to a topic, or waiting for a message, does not complete within the specified timeout period. It ensures that long-running or stalled processes can be gracefully handled.

    Attributes:
        message (str): A detailed description of the timeout error.
        timeout (float): The duration (in seconds) after which the timeout occurred.
    """

    def __init__(self, message="Operation timed out.", timeout=None):
        self.timeout = timeout
        if timeout:
            message += f" (Timeout: {timeout} seconds)"
        super().__init__(message)


class ConnectionErrorException(Exception):
    """
    Raised when the connection to the MQTT broker fails.
    
    Attributes:
        host (str): The broker host.
        port (int): The broker port.
        message (str): Additional details about the connection error.
    """

    def __init__(self, host, port, message="Failed to connect to the MQTT broker"):
        self.host = host
        self.port = port
        super().__init__(f"{message} at {host}:{port}")