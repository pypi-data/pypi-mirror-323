import os
import socket
import select
import json
import logging
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any, List

class Messenger:
    """Asynchronous Unix domain socket client for JSON message communication.
    
    This class implements a full-featured messaging system using Unix domain sockets,
    providing a robust foundation for IPC (Inter-Process Communication) with support
    for asynchronous operations and type-based message routing.

    Features:
        * Asynchronous message sending and receiving
        * JSON-based message protocol
        * Type-based message routing with callback system
        * Automatic connection management and retry
        * Context manager interface

    Example:
        Basic usage as a context manager::

            def handle_response(message):
                print(f"Received response: {message}")

            socket_path = "/tmp/server.sock"
            client_path = "/tmp/client.sock"

            with Messenger(socket_path, client_path) as messenger:
                messenger.add_listener("response", handle_response)
                messenger.send_message({
                    "type": "request",
                    "data": {"action": "get_status"}
                })

    Protocol:
        Messages are JSON objects with a required 'type' field::

            {
                "type": "message_type",
                "data": {
                    // Optional message-specific data
                }
            }

        Messages are delimited by newlines when transmitted.

    Note:
        The class automatically handles connection lifecycle, including cleanup
        of socket files and proper resource management.
    
    Args:
        socket_server: Path to the Unix domain socket server (default: '\0ai-message-control.server')
        socket_client: Path to the Unix domain socket client (default: '\0ai-message-control.client')
        connection_retry_interval: Time in seconds between connection attempts (default: 10.0)
        connection_timeout: Maximum time in seconds to wait for connection (default: 120.0)
    """

    def __init__(
        self,
        socket_server: str = "\0ai-message-control.server",
        socket_client: str = "\0ai-message-control.client",
        connection_retry_interval: float = 10.0,
        connection_timeout: float = 120.0
    ):
        self.socket_server = socket_server
        self.socket_client = socket_client
        self.connection_retry_interval = connection_retry_interval
        self.connection_timeout = connection_timeout
        self.listeners: Dict[str, List[Callable[[dict], None]]] = {}
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.send_queue = queue.Queue()
        self.io_thread = None
       
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
       
        # Buffer for incoming data
        self.recv_buffer = b''
       
    def _wait_for_socket(self) -> bool:
        """
        Wait for the socket connection to become available.
        
        Attempts to connect repeatedly until successful or timeout is reached.
       
        Returns:
            bool: True if connection was established, False if timeout was reached
        """
        start_time = time.time()
        attempt = 1
       
        while True:
            self.logger.info(f"Connection attempt {attempt}")
            try:
                if self._connect():
                    return True
                   
            except socket.error as e:
                self._close_socket()
                
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.connection_timeout:
                    self.logger.error("Connection timeout reached")
                    return False
                   
                self.logger.warning(
                    f"Socket not available, retrying in {self.connection_retry_interval} seconds. "
                    f"Error: {e}"
                )
                time.sleep(self.connection_retry_interval)
                attempt += 1
       
    def _connect(self) -> bool:
        """
        Establish connection to the Unix domain socket server.
        
        Creates a new UDP socket, binds it to the client address, and attempts
        to verify connectivity with the server.
       
        Returns:
            bool: True if connection was successfully established
            
        Raises:
            socket.error: If socket operations fail
        """ 
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(self.socket_client)
        self.sock.setblocking(False)

        # Try sending a test message to verify connection
        self.sock.sendto(b'', self.socket_server)
        self.logger.info(f"Connected to socket at {self.socket_server}")
        self.logger.info(f"Client socket bound to {self.socket_client}")

        return True

    def _close_socket(self):
        """Close the socket connection and release resources."""
        if self.sock is not None:
            self.sock.close()
            if not self.socket_client.startswith('\0') and os.path.exists(self.socket_client):
                try:
                    os.unlink(self.socket_client)
                except OSError:
                    pass
            self.sock = None

    def start(self):
        """
        Start the asynchronous I/O handling thread.
        
        Initiates the connection and starts a background thread for handling
        message sending and receiving. If already running, does nothing.
        """
        if self.running:
            return
           
        # Start connection in background thread
        self.running = True
        self.io_thread = threading.Thread(target=self._connect_and_run)
        self.io_thread.daemon = True
        self.io_thread.start()

    def _connect_and_run(self):
        """Background thread that handles connection and I/O loop."""
        if not self._wait_for_socket():
            self.logger.error(f"Failed to connect to socket after {self.connection_timeout} seconds")
            self.stop()
            return
            
        self._io_loop()
       
    def stop(self):
        """
        Stop the asynchronous I/O handling thread and cleanup resources.
        
        Handles both external stops (from other threads) and internal stops
        (from within the I/O thread itself).
        """
        self.running = False
        
        # Clear queues and buffers
        self.recv_buffer = b''
        while not self.send_queue.empty():
            try:
                self.send_queue.get_nowait()
            except queue.Empty:
                break

        # Only join if we're not stopping internally
        if self.io_thread and self.io_thread.is_alive() and threading.current_thread() != self.io_thread:
            self.io_thread.join(timeout=1)
            
        self._close_socket()
           
    def send_message(self, message: Dict[str, Any]):
        """
        Queue a message for asynchronous transmission.
        
        The message will be converted to JSON and sent when the socket
        is available for writing.
       
        Args:
            message: Dictionary containing the message data to be JSON-encoded
        """
        self.logger.info(f"Queueing message: {message}")
        self.send_queue.put(message)
       
    def _io_loop(self):
        """Main I/O loop handling both sending and receiving."""
        while self.running:
            try:
                readable, writable, _ = select.select(
                    [self.sock],
                    [self.sock] if not self.send_queue.empty() else [],
                    [],
                    0.1  # Small timeout to prevent busy waiting
                )
                
                # Handle incoming messages
                if readable:
                    try:
                        data, _ = self.sock.recvfrom(4096)
                        if not data:  # Connection closed
                            self.logger.warning("Server closed connection")
                            break

                        self._handle_received_data(data)
                            
                    except socket.error as e:
                        self.logger.error(f"Error receiving data: {e}")
                        break
                        
                # Handle outgoing messages
                if writable:
                    try:
                        message = self.send_queue.get_nowait()
                        data = json.dumps(message).encode('utf-8')
                        self.sock.sendto(data, self.socket_server)
                    except queue.Empty:
                        pass
                    except socket.error as e:
                        self.logger.error(f"Error sending data: {e}")
                        break
                        
            except Exception as e:
                self.logger.error(f"Error in I/O loop: {e}")
                break
       
    def _parse_buffer(self) -> list[dict]:
        """
        Parse received data buffer for complete JSON messages.
        
        Processes the internal receive buffer to extract complete JSON messages,
        handling partial messages and maintaining the buffer state.
        
        Returns:
            list[dict]: List of complete parsed JSON messages
        """
        messages = []
        try:
            # Convert buffer to string
            data = self.recv_buffer.decode('utf-8')
            # Find complete messages
            while True:
                try:
                    # Try to decode a complete JSON object
                    message, index = json.JSONDecoder().raw_decode(data)
                    messages.append(message)
                    # Remove processed data from buffer
                    data = data[index:].lstrip()
                    if not data:
                        break
                except json.JSONDecodeError:
                    break
                    
            # Update buffer with remaining incomplete data
            self.recv_buffer = data.encode('utf-8')
            
        except UnicodeDecodeError:
            # Keep buffer unchanged if decode fails
            pass
            
        return messages

    def _handle_received_data(self, data: bytes) -> None:
        """
        Process received socket data and dispatch to message handlers.
        
        Accumulates received data in the buffer, extracts complete JSON messages,
        and calls registered callbacks for matching message types.
        
        Args:
            data: Raw bytes received from the socket
        """
        self.recv_buffer += data
        
        # Process all complete messages in buffer
        for message in self._parse_buffer():
            try:
                # Extract message type from the message
                message_type = message.get('type')
                if message_type and message_type in self.listeners:
                    for callback in self.listeners[message_type]:
                        try:
                            callback(message)
                        except Exception as e:
                            self.logger.error(f"Error in listener callback: {e}")
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
               
    def add_listener(self, message_type: str, callback: Callable[[dict], None]) -> None:
        """Register a callback function for a specific message type.
        
        Multiple callbacks can be registered for the same message type and will
        be executed in registration order when matching messages are received.
        
        Args:
            message_type: String identifier for the message type
            callback: Function to call when matching messages are received
            
        Example:
            Registering multiple callbacks::
            
                def log_message(msg):
                    print(f"Logged: {msg}")
                    
                def process_message(msg):
                    # Process the message
                    pass
                    
                messenger.add_listener("status", log_message)
                messenger.add_listener("status", process_message)
        """
        if message_type not in self.listeners:
            self.listeners[message_type] = []
        self.listeners[message_type].append(callback)

    def remove_listener(self, message_type: str, callback: Callable[[dict], None]) -> bool:
        """
        Unregister a callback function for a specific message type.
        
        Args:
            message_type: String identifier for the message type
            callback: The callback function to remove
            
        Returns:
            bool: True if the callback was found and removed, False otherwise
        """
        if message_type in self.listeners and callback in self.listeners[message_type]:
            self.listeners[message_type].remove(callback)
            if not self.listeners[message_type]:
                del self.listeners[message_type]
            return True
        return False
               
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
       
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
