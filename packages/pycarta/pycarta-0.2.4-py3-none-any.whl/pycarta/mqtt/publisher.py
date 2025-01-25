import os
import json
import time
import asyncio
import socket
import inspect
from functools import wraps
from typing import Callable, Any, Optional
from .credential import BaseMqttAuthenticator
from .connection import (
    MQTTConnection, 
    PubSubStopIteration, 
    PublishError, 
    SerializationError, 
    pclient, 
    logger
)

def _default_serializer(content: Any) -> str:
    """Serialize content to JSON or string."""
    try:
        # Attempt to serialize using a Pydantic model's method
        return content.model_dump_json()
    except AttributeError:
        logger.debug("[publish] Content is not a Pydantic BaseModel.")
    try:
        # Attempt to serialize as JSON
        return json.dumps(content)
    except (TypeError, ValueError) as e:
        logger.debug(f"[publish] Content is not JSON serializable: {e}")
        raise SerializationError(f"Failed to serialize content: {e}")
    return str(content)

    
class publish(MQTTConnection):
    """
    Decorator for synchronous publishing to an MQTT topic.
    """

    FIRST_RETRY_DELAY = int(os.environ.get("FIRST_RETRY_DELAY", 1))
    RETRY_RATE = int(os.environ.get("RETRY_RATE", 2))
    MAX_RETRY_COUNT = int(os.environ.get("MAX_RETRY_COUNT", 12))
    MAX_RETRY_DELAY = int(os.environ.get("MAX_RETRY_DELAY", 60))

    def __init__(self,
                 topic: str,
                 *,
                 host: str = "localhost",
                 port: int = 1883,
                 serializer: Callable | None = None,
                 lazy: bool = True,
                 qos: int = 0,
                 authenticator: BaseMqttAuthenticator | None = None):
        """
        Args:
            topic (str): MQTT topic for publishing.
            host (str): MQTT broker host. Default is 'localhost'.
            port (int): MQTT broker port. Default is 1883.
            serializer (Callable | None): Function to serialize messages. Defaults to JSON or string conversion.
            lazy (bool): If False, connect to the broker immediately. Defaults to True.
            qos (int): Quality of Service level for MQTT. Defaults to 0.
            authenticator (BaseMqttAuthenticator): Optional TLS authenticator. Default is None.
        """
        super().__init__(topic, host=host, port=port, authenticator=authenticator)
        self.serializer = serializer or _default_serializer
        self.qos = qos
        if not lazy:
            self.connect()

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"[sync publish] Preparing to publish to topic {self.topic}.")
            self.connect()
            result = func(*args, **kwargs)
            try:
                payload = self.serializer(result)
            except SerializationError as e:
                logger.error(f"[sync publish] Serialization error: {e}")
                raise e

            retry_count = 0
            retry_delay = self.FIRST_RETRY_DELAY

            while retry_count < self.MAX_RETRY_COUNT:
                try:
                    rc, mid = self.client.publish(self.topic, payload, qos=self.qos)
                    if rc == pclient.MQTT_ERR_SUCCESS:
                        logger.info(f"[sync publish] Successfully published to {self.topic}: {payload}")
                        break
                except Exception as e:
                    logger.error(f"[sync publish] Unexpected error: {e}")
                    raise PublishError() from e

                logger.warning(f"[sync publish] Failed to publish, rc={rc}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * self.RETRY_RATE, self.MAX_RETRY_DELAY)
                retry_count += 1
            else:
                logger.error(f"[sync publish] Failed to publish after {retry_count} retries.")
                raise PublishError()

            self.disconnect()
            return result

        return wrapper


class async_publish(MQTTConnection):
    """
    Decorator for asynchronous publishing to an MQTT topic.
    """

    FIRST_RETRY_DELAY = int(os.environ.get("FIRST_RETRY_DELAY", 1))
    RETRY_RATE = int(os.environ.get("RETRY_RATE", 2))
    MAX_RETRY_COUNT = int(os.environ.get("MAX_RETRY_COUNT", 12))
    MAX_RETRY_DELAY = int(os.environ.get("MAX_RETRY_DELAY", 60))

    def __init__(self,
                 topic: str,
                 *,
                 host: str = "localhost",
                 port: int = 1883,
                 serializer: Callable | None = None,
                 lazy: bool = True,
                 qos: int = 0,
                 authenticator: BaseMqttAuthenticator | None = None):
        """
        Args:
            topic (str): MQTT topic for publishing.
            host (str): MQTT broker host. Default is 'localhost'.
            port (int): MQTT broker port. Default is 1883.
            serializer (Callable | None): Function to serialize messages. Defaults to JSON or string conversion.
            lazy (bool): If False, connect to the broker immediately. Defaults to True.
            qos (int): Quality of Service level for MQTT. Defaults to 0.
            authenticator (BaseMqttAuthenticator): Optional TLS authenticator. Default is None.
        """
        super().__init__(topic, host=host, port=port, authenticator=authenticator)
        self.serializer = serializer or _default_serializer
        self.qos = qos
        if not lazy:
            self.connect()

    async def connect_async(self):
        """Asynchronously connect to the MQTT broker."""
        if not self.client.is_connected():
            await asyncio.to_thread(self.connect)
            self.client.loop_start()
            logger.debug(f"[async publish] Connected to {self.host}:{self.port}")

    async def disconnect_async(self):
        """Asynchronously disconnect from the MQTT broker."""
        if self.client.is_connected():
            await asyncio.to_thread(self.disconnect)
            self.client.loop_stop()
            logger.debug(f"[async publish] Disconnected from {self.host}:{self.port}")

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug(f"[async publish] Preparing to publish to topic {self.topic}.")

            if not self.client.is_connected():
                try:
                    await self.connect_async()
                except socket.error as e:
                    logger.error(f"[async publish] Connection error: {e}")
                    raise PublishError() from e

            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else await asyncio.to_thread(func, *args, **kwargs)
            try:
                payload = self.serializer(result)
            except SerializationError as e:
                logger.error(f"[async publish] Serialization error: {e}")
                raise e

            retry_count = 0
            retry_delay = self.FIRST_RETRY_DELAY

            while retry_count < self.MAX_RETRY_COUNT:
                try:
                    rc, mid = await asyncio.to_thread(self.client.publish, self.topic, payload, qos=self.qos)
                    if rc == pclient.MQTT_ERR_SUCCESS:
                        logger.info(f"[async publish] Successfully published to {self.topic}: {payload}")
                        return result
                except Exception as e:
                    logger.error(f"[async publish] Unexpected error: {e}")
                    raise PublishError() from e

                logger.debug(f"[async publish] Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * self.RETRY_RATE, self.MAX_RETRY_DELAY)
                retry_count += 1

            logger.error(f"[async publish] Failed to publish after {retry_count} retries.")
            raise PublishError()

        return wrapper
