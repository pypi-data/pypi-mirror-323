"""
Test for MQTT functionalities using Paho MQTT with TLS authentication.

This test suite reads CA certificate, client certificate, and private key 
from specified files and uses them to configure a `BilateralCredentialAuthenticator`.

Required Certificates:
- `mosquitto.org.crt`: CA certificate
- `client.crt`: Client certificate
- `client.key`: Private key

For details on obtaining these certificates, refer to:

https://test.mosquitto.org/ssl/

Usage:
To run the tests with the necessary certificates, use the following command 
from the repository root:

    pytest test_mqtt.py \
        --ca_cert=mqtt/cert-mosquitto/mosquitto.org.crt \
        --client_cert=mqtt/cert-mosquitto/client.crt \
        --client_key=mqtt/cert-mosquitto/client.key

Ensure the paths to the certificate files are correct.
"""
import socket
import threading
import asyncio
import uuid
import time
import pytest
from pathlib import Path

# Import publisher and subscriber decorators
from pycarta.mqtt.publisher import publish, async_publish
from pycarta.mqtt.subscriber import subscribe, async_subscribe
from pycarta.mqtt.connection import PubSubStopIteration
from pycarta.mqtt.credential import BilateralCredentialAuthenticator

# Define broker configurations, local and remote mosquitto brokers with and without credentials
BROKERS = [
    {
        "label": "mosquitto_local",
        "host": "localhost",
        "port": 1883,
    },
    {
        "label": "mosquitto_remote",
        "host": "test.mosquitto.org",
        "port": 1883,
    },
    {
        "label": "mosquitto_remote_cred",
        "host": "test.mosquitto.org",
        "port": 8884,
    },
]

@pytest.fixture
def maybe_auth(broker, tls_credentials):
    """
    Return a BilateralCredentialAuthenticator only for 'mosquitto_remote_cred' broker, otherwise return None. This time, we use the from_cert_files() class method (Approach #1) to pass file paths to the BilateralCredentialAuthenticator.
    """
    if broker["label"] != "mosquitto_remote_cred":
        return None

    ca_path = tls_credentials["ca_cert_path"]
    cert_path = tls_credentials["client_cert_path"]
    key_path = tls_credentials["client_key_path"]

    # Ensure all paths exist before trying to create the authenticator
    if not ca_path or not Path(ca_path).is_file():
        pytest.skip(f"CA certificate file not found: {ca_path}")
    if not cert_path or not Path(cert_path).is_file():
        pytest.skip(f"Client certificate file not found: {cert_path}")
    if not key_path or not Path(key_path).is_file():
        pytest.skip(f"Client key file not found: {key_path}")

    return BilateralCredentialAuthenticator.from_cert_files(
        ca_cert=ca_path,
        cert=cert_path,
        key=key_path,
    )

@pytest.fixture(scope="session")
def check_local_broker():
    """
    Check if the local Mosquitto broker is running (port 1883).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1)
        s.connect(("localhost", 1883))
    except socket.error:
        s.close()
        return False
    else:
        s.close()
        return True

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(params=BROKERS, ids=lambda b: b["label"])
def broker(request, check_local_broker):
    """
    Parameterize tests to run against BROKERS (mosquitto_local, mosquitto_remote, mosquitto_remote_cred).
    """
    broker = request.param
    if broker["label"] == "mosquitto_local" and not check_local_broker:
        pytest.skip("Local Mosquitto broker is not running.")
    return broker

def test_publish_subscribe_sync(broker, maybe_auth):
    received_messages = []
    returned_message = None
    message_event = threading.Event()
    test_message = {"test": "sync message"}
    topic = f"test/topic/{uuid.uuid4()}"

    @subscribe(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    def handle_message(msg):
        nonlocal returned_message
        print(f"[Test] handle_message called with msg: {msg}")
        received_messages.append(msg)
        returned_message = msg
        message_event.set()

    def run_subscriber():
        try:
            subscriber = handle_message.__iter__()
            next(subscriber)
        except PubSubStopIteration:
            pass
        finally:
            message_event.set()

    # Start the subscriber in a separate thread
    subscriber_thread = threading.Thread(target=run_subscriber, daemon=True)
    subscriber_thread.start()

    # Allow some time for the subscriber to connect and subscribe
    time.sleep(1)

    # Define publisher function
    @publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    def publish_message():
        return test_message

    # Publish the message
    publish_message()

    # Wait for the message to be received with a timeout
    assert message_event.wait(timeout=30), "Did not receive message in time."

    # Verify the returned message matches the published message
    assert returned_message == test_message, f"Returned message does not match. Expected {test_message}, got {returned_message}."

    # Verify the received message list contains the published message
    assert test_message in received_messages, "Received messages list does not contain the published message."

@pytest.mark.asyncio
async def test_publish_subscribe_async(broker, maybe_auth):
    received_messages = []
    returned_message = None
    message_event = asyncio.Event()
    test_message = {"test": "async message"}
    topic = f"test/topic/{uuid.uuid4()}"

    # Define subscriber function
    @async_subscribe(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def handle_message(msg):
        nonlocal returned_message
        print(f"[Test Subscriber] Received message: {msg}")
        received_messages.append(msg)
        returned_message = msg
        message_event.set()

    # Start subscriber as an asynchronous task
    subscriber_task = asyncio.create_task(handle_message())

    # Allow some time for the subscriber to connect and subscribe
    await asyncio.sleep(1)

    # Define publisher function
    @async_publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def publish_message():
        return test_message

    # Publish the message
    await publish_message()

    # Wait for the message to be received with a timeout
    try:
        await asyncio.wait_for(message_event.wait(), timeout=10)
    except asyncio.TimeoutError:
        pytest.fail("Did not receive message in time.")
    else:
        # Verify the returned message matches the published message
        assert returned_message == test_message, (
            f"Returned message does not match. Expected {test_message}, got {returned_message}."
        )

        # Verify the received message list contains the published message
        assert test_message in received_messages, "Received messages list does not contain the published message."

    # Cancel the subscriber task to clean up
    subscriber_task.cancel()
    try:
        await subscriber_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_async_mqtt_publish_subscribe_calculation(broker, maybe_auth):
    """
    Test the complete asynchronous MQTT publish and subscribe flow by publishing multiple messages and verifying that the subscriber receives and processes them correctly.
    """
    # Initialize a unique topic for this test to avoid interference
    topic = f"test/main_example/{uuid.uuid4()}"
    
    # Define the asynchronous publisher function
    @async_publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def add(lhs, rhs):
        """Publishes the sum of lhs and rhs to the specified topic."""
        return lhs + rhs
    
    # Initialize a list to store received messages
    received_messages = []
    
    # Define the asynchronous subscriber function
    @async_subscribe(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def double(x):
        """
        Subscriber that doubles the received value and appends it to received_messages.
        """
        print(f"[Test Subscriber] Received message: {x}")
        try:
            result = int(x) * 2
        except ValueError:
            print(f"[Test Subscriber] Failed to convert message to int: {x}")
            return None
        print(f"[Test Subscriber] Doubled value: {result}")
        received_messages.append(result)
        return result  # Ensure the message is returned for the iterator
    
    async def main_test():
        print("[Test Main] Starting MQTT subscription...")
        
        # Start the subscriber by creating an asynchronous iterator
        subscriber_iter = double.__aiter__()
        
        # Allow some time for the subscriber to connect and subscribe
        await asyncio.sleep(2)  # Increased delay
        
        # Define a list of values to publish
        test_values = [0, 5, 10, 15, 20]
        
        # Publish messages sequentially with increased delays
        for value in test_values:
            await add(value, value)  # Publishes lhs + rhs
            await asyncio.sleep(0.5)  # Increased delay between publishes
        
        print("[Test Main] Published all messages.")
        
        # Initialize a counter for received messages
        received_count = 0
        expected_count = len(test_values)
        
        # Process incoming messages from the subscriber using async for
        async for message in subscriber_iter:
            if message is not None:
                print(f"[Test Main] Processed message result: {message}")
                received_count += 1
                # Exit condition for testing purposes
                if received_count >= expected_count:
                    print("[Test Main] Received all expected messages. Exiting.")
                    break
        
        # Cleanup: Stop the subscriber iterator
        try:
            await subscriber_iter.__anext__()  # This should raise StopAsyncIteration
        except StopAsyncIteration:
            print("[Test Main] Subscriber iteration stopped gracefully.")
    
    # Run the main_test coroutine
    await main_test()
    
    # Define the expected messages after processing (doubled values)
    expected_messages = [0, 20, 40, 60, 80]
    
    # Verify that all expected messages were received and processed
    assert received_messages == expected_messages, (
        f"Expected received messages to be {expected_messages}, but got {received_messages}"
    )
    
    print("[Test Main] Subscription and publishing test completed successfully.")


@pytest.mark.asyncio
async def test_async_mqtt_publish_subscribe_monitoring(broker, maybe_auth):
    """
    Test the asynchronous MQTT publish and subscribe flow by publishing messages
    and verifying that the subscriber receives and processes them correctly.
    """
    mu = 12.34
    sigma = 3.45
    lower_bound, upper_bound = (mu - 2.0 * sigma, mu + 2.0 * sigma)  # [5.44, 19.24]
    test_values = [7, 9, 11, 13]
    topic = f"machine/sensor/{uuid.uuid4()}"

    # Define the asynchronous publisher functions
    @async_publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def add(lhs, rhs):
        """Publishes the sum of lhs and rhs to the specified topic."""
        return lhs + rhs

    @async_publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def on_error():
        """Publishes 'STOP' to the specified topic."""
        return "STOP"

    @async_publish(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def no_error():
        """Publishes 'CONTINUE' to the specified topic."""
        return "CONTINUE"

    # Initialize a list to store received messages
    received_messages = []
    returned_message = None
    message_event = asyncio.Event()

    # Initialize an event to signal the publisher to stop
    publisher_should_stop = asyncio.Event()

    # Define the asynchronous subscriber function
    @async_subscribe(
        topic=topic,
        host=broker["host"],
        port=broker["port"],
        authenticator=maybe_auth
    )
    async def get_sensor_value(x):
        nonlocal returned_message
        print(f"[Async Subscriber] Received message: {x}")
        try:
            # Attempt to convert the message to float
            x_float = float(x)
            received_messages.append(x_float)
            returned_message = x_float
        except ValueError:
            print(f"[Async Subscriber] Received non-numeric message: {x}")
            return None
        # Check error condition
        if not lower_bound < x_float < upper_bound:
            await on_error()
            print(f"[Async Subscriber] Published 'STOP' due to out-of-bounds value: {x_float}")
            message_event.set()
            publisher_should_stop.set()  # Signal the publisher to stop
            raise StopAsyncIteration
        else:
            await no_error()
            print(f"[Async Subscriber] Published 'CONTINUE' for value: {x_float}")

    async def run_subscriber():
        try:
            async for _ in get_sensor_value:
                pass
        except StopAsyncIteration:
            pass
        finally:
            message_event.set()

    async def publish_messages():
        for value in test_values:
            if publisher_should_stop.is_set():
                print("[Async Publisher] Received stop signal. Stopping publishing.")
                break
            result = await add(value, value)  # Publishes lhs + rhs
            print(f"[Async Publisher] Published sensor value: {result}")
            await asyncio.sleep(3)  # 3-second delay between publishes
        print("[Async Publisher] Published all messages or stopped early.")

    # Start the subscriber task
    subscriber_task = asyncio.create_task(run_subscriber())

    # Wait to ensure subscriber is ready
    await asyncio.sleep(2)  # Increased delay to allow subscriber to connect

    # Start the publisher task
    publisher_task = asyncio.create_task(publish_messages())

    # Wait for the 'STOP' message to be received
    try:
        await asyncio.wait_for(message_event.wait(), timeout=20)  # Increased timeout for remote broker
    except asyncio.TimeoutError:
        pytest.fail("Did not receive 'STOP' message in time.")
    else:
        # Cancel the publisher task to prevent further messages
        publisher_task.cancel()
        try:
            await publisher_task
        except asyncio.CancelledError:
            pass

        # Define expected messages after processing up to 'STOP'
        # For test_values = [7,9,11,13], add publishes [14,18,22,26]
        # get_sensor_value processes [14.0, 18.0, 22.0], 'STOP' at 22
        expected_messages = [14.0, 18.0, 22.0]

        # Verify that all expected messages were received and processed up to 'STOP'
        assert received_messages == expected_messages, (
            f"Expected received messages to be {expected_messages}, but got {received_messages}"
        )

        print("[Async Test] Subscription and publishing test completed successfully.")