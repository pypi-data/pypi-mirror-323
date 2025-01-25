import os
import json
import time
import asyncio
from queue import Queue, Empty
from typing import Any, Callable, Optional
from .credential import BaseMqttAuthenticator
from .connection import (
    MQTTConnection,
    PubSubStopIteration,
    TimeoutException,
    SubscribeError,
    SerializationError,
    logger
)

# TODO: Need to add a START/END keyword to the publisher/subscriber. The argument against this was that publishing STOP would stop everything and this could be better thought of as the start and end of an array of values. It is beyond the scope of the MVP, because a user could handle that themselves using a custom serializer, but a feature worth adding after authentication.

def _default_deserializer(message: str) -> Any:
    """Deserialize message to Pydantic model, JSON, or return raw string."""
    try:
        # Attempt to reconstruct a Pydantic model if relevant
        return json.loads(message)
    except Exception as e:
        logger.debug(f"[subscriber] Message is not deserializable to a Pydantic model: {e}")
    try:
        # Check if message can be deserialized as JSON
        return json.loads(message)
    except json.JSONDecodeError:
        logger.debug("[subscriber] Message not JSON-deserializable.")
    return message
    

class subscribe:
    """Decorator for synchronous MQTT subscriptions."""
    class Task(MQTTConnection):
        """Handles synchronous MQTT subscription tasks."""

        def __init__(self,
                     topic: str,
                     *,
                     host: str = "localhost",
                     port: int = 1883,
                     authenticator: BaseMqttAuthenticator | None = None,
                     qos: int = 0,
                     deserializer: Callable | None = None):
            super().__init__(topic, host=host, port=port, authenticator=authenticator)
            self.deserializer = deserializer or _default_deserializer
            self.qos = qos
            self.result_queue = Queue()
            self.func: Callable | None = None

        def connect(self):
            """Connect to the MQTT broker and subscribe to the topic."""
            self.client.on_message = self._on_message
            super().connect()
            self.client.subscribe(self.topic, qos=self.qos)
            logger.debug(f"[sync subscribe] Subscribed to topic: {self.topic}")

        def _on_message(self, client, userdata, msg):
            """Handle incoming MQTT messages."""
            try:
                raw_message = msg.payload.decode()
                logger.debug(f"[sync subscribe] Received raw message: {raw_message}")
                deserialized_message = self.deserializer(raw_message)
                processed_message = self.func(deserialized_message) if self.func else deserialized_message
                self.result_queue.put(processed_message)
                logger.debug(f"[sync subscribe] Processed message: {processed_message}")
            except Exception as e:
                logger.error(f"[sync subscribe] Error processing message: {e}")

        def _poll(self, single_message=False):
            """Poll for messages from the result queue."""
            start_time = time.perf_counter()
            while True:
                elapsed = time.perf_counter() - start_time
                remaining_timeout = max(self.POLLING_TIMEOUT - elapsed, 0)
                if remaining_timeout <= 0:
                    break
                try:
                    return self.result_queue.get(timeout=self.POLLING_INTERVAL)
                except Empty:
                    logger.debug(f"[sync subscribe] Polling... Timeout in {int(remaining_timeout)} seconds.")

            if single_message:
                logger.info(f"[sync subscribe] Timeout after {self.POLLING_TIMEOUT} seconds. No messages received.")
                raise TimeoutException(f"No messages received in {self.POLLING_TIMEOUT} seconds.")
            return None

        def __call__(self):
            """Process a single message."""
            self.connect()
            self.client.loop_start()
            try:
                return self._poll(single_message=True)
            finally:
                self.client.loop_stop()
                self.disconnect()

        def __iter__(self):
            """Iterator for processing messages."""
            self.connect()
            self.client.loop_start()
            return self

        def __next__(self):
            try:
                return self._poll(single_message=True)
            except (KeyboardInterrupt, TimeoutException):
                self.client.loop_stop()
                self.disconnect()
                raise StopIteration

    def __init__(self,
             topic: str,
             *,
             host: str = "localhost",
             port: int = 1883,
             authenticator: BaseMqttAuthenticator | None = None,
             qos: int = 0,
             deserializer: Callable | None = None):
        self.task = subscribe.Task(
            topic,
            host=host,
            port=port,
            authenticator=authenticator,
            qos=qos,
            deserializer=deserializer
        )

    def __call__(self, func: Callable | None = None):
        if func is not None:
            self.task.func = func
        return self.task


class async_subscribe:
    """Decorator for asynchronous MQTT subscriptions."""

    class Task(MQTTConnection):
        """Handles asynchronous MQTT subscription tasks."""

        def __init__(self,
                     topic: str,
                     *,
                     host: str = "localhost",
                     port: int = 1883,
                     authenticator: BaseMqttAuthenticator | None = None,
                     qos: int = 0,
                     deserializer: Callable[[str], Any] | None = None):
            """Initialize the subscription task."""
            super().__init__(topic, host=host, port=port, authenticator=authenticator)
            self.deserializer = deserializer or _default_deserializer
            self.qos=qos
            self.result_queue = asyncio.Queue()
            self.func: Callable[[Any], Any] | None = None
            self.connected = False
            self.connect_task: asyncio.Task | None = None  # Reference to the connection task
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.get_event_loop()

        async def clear_queue(self):
            """Clear all items in the result queue."""
            logger.debug(f"[async subscribe] Clearing the queue. Current size: {self.result_queue.qsize()}")
            while not self.result_queue.empty():
                try:
                    item = self.result_queue.get_nowait()
                    self.result_queue.task_done()
                    logger.debug(f"[async subscribe] Removed item from queue: {item}")
                except asyncio.QueueEmpty:
                    logger.debug("[async subscribe] Queue is empty now.")
                    break
            logger.debug("[async subscribe] Queue cleared.")

        async def connect_async(self):
            """Connect to the MQTT broker asynchronously."""
            if not self.connected:
                logger.debug(f"[async subscribe] Connecting to {self.host}:{self.port}.")
                await asyncio.to_thread(self.connect)
                self.client.on_message = self._on_message
                self.client.subscribe(self.topic, qos=self.qos)
                self.client.loop_start()
                self.connected = True
                logger.debug(f"[async subscribe] Subscribed to topic: {self.topic}")

        async def disconnect_async(self, clear_queue=False):
            """Disconnect from the MQTT broker asynchronously."""
            if self.connected:
                logger.debug(f"[async subscribe] Disconnecting from {self.host}:{self.port}.")
                await asyncio.to_thread(self.disconnect)
                self.client.loop_stop()
                self.connected = False
                if clear_queue:
                    await self.clear_queue()
                logger.debug("[async subscribe] Disconnected from MQTT broker.")

        def _on_message(self, client, userdata, msg):
            """Handle incoming messages from the broker."""
            try:
                raw_message = msg.payload.decode()
                logger.debug(f"[async subscribe] Received raw message: {raw_message}")
                deserialized_message = self.deserializer(raw_message)
                asyncio.run_coroutine_threadsafe(self._process_message(deserialized_message), self.loop)
            except Exception as e:
                logger.error(f"[async subscribe] Error processing message: {e}")

        async def _process_message(self, message):
            """Process incoming messages using the decorated function."""
            try:
                if self.func:
                    if asyncio.iscoroutinefunction(self.func):
                        result = await self.func(message)
                    else:
                        result = await asyncio.to_thread(self.func, message)
                    logger.debug(f"[async subscribe] Processed message result: {result}")
                    await self.result_queue.put(result)
            except StopAsyncIteration:
                logger.debug("[async subscribe] StopAsyncIteration received. Ending subscription.")
            except Exception as e:
                logger.error(f"[async subscribe] Error processing message: {e}")

        async def _poll(self, single_message=False):
            """Poll for messages from the result queue."""
            start_time = time.perf_counter()
            while True:
                elapsed = time.perf_counter() - start_time
                remaining_timeout = max(self.POLLING_TIMEOUT - elapsed, 0)
                if remaining_timeout <= 0:
                    break
                try:
                    return await asyncio.wait_for(self.result_queue.get(), timeout=self.POLLING_INTERVAL)
                except asyncio.TimeoutError:
                    logger.debug(f"[async subscribe] Polling... Timeout in {int(remaining_timeout)} seconds.")

            if single_message:
                logger.info(f"[async subscribe] Timeout after {self.POLLING_TIMEOUT} seconds. No messages received.")
                raise TimeoutException(f"No messages received in {self.POLLING_TIMEOUT} seconds.")
            return None

        async def __call__(self):
            """Process a single message asynchronously with graceful timeout handling."""
            logger.debug("[async subscribe] Starting single message processing.")
            await self.connect_async()
            try:
                return await self._poll()
            except KeyboardInterrupt:
                logger.info("[async subscribe] Keyboard interrupt received. Stopping subscriber.")
            except asyncio.TimeoutError:
                logger.warning("[async subscribe] Timeout occurred while waiting for a message.")
                return None  # Or handle it as needed
            finally:
                await self.disconnect_async()

        def __aiter__(self):
            """Make the task class an async iterator."""
            if not self.connect_task or self.connect_task.done():
                self.connect_task = asyncio.create_task(self.connect_async())
            return self

        async def __anext__(self):
            """Retrieve the next message asynchronously."""
            try:
                message = await self._poll(single_message=True)
                return message
            except TimeoutException:
                logger.debug("[async subscribe] No more messages. Stopping iteration.")
                await self._cleanup()
                raise StopAsyncIteration
            except Exception as e:
                logger.error(f"[async subscribe] Unexpected error during iteration: {e}")
                await self._cleanup()
                raise StopAsyncIteration

        async def _cleanup(self):
            """Clean up resources after iteration ends."""
            if self.connect_task and not self.connect_task.done():
                self.connect_task.cancel()
                try:
                    await self.connect_task
                except asyncio.CancelledError:
                    logger.debug("[async subscribe] Connection task cancelled.")
            await self.disconnect_async(clear_queue=True)
            self.connect_task = None

    def __init__(self,
             topic: str,
             *,
             host: str = "localhost",
             port: int = 1883,
             authenticator: BaseMqttAuthenticator | None = None,
             qos: int = 0,
             deserializer: Callable[[str], Any] | None = None):
        self.task = async_subscribe.Task(
            topic,
            host=host,
            port=port,
            authenticator=authenticator,
            qos=qos,
            deserializer=deserializer
        )

    def __call__(self, func: Callable[[Any], Any] | None = None):
        """Set the decorated function to process messages."""
        if func is not None:
            self.task.func = func
        return self.task
