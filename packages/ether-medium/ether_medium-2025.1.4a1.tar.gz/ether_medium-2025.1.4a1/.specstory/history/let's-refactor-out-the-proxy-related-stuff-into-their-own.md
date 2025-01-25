## SpecStory

## Let's refactor out the proxy related stuff into their own (11/5/2024, 2:16:26 PM)

_**User**_

Let's refactor out the proxy related stuff into their own _proxy.py file.

---

_**Assistant**_

I'll help you refactor the proxy-related code into a new `_proxy.py` file. Here's how we'll do it:

1. First, let's create the new file:

```python:src/ether/_proxy.py
import zmq
import logging
import signal
import uuid
from multiprocessing import Event, Process
import os
import tempfile
import atexit
import time

from ._utils import _ETHER_SUB_PORT, _ETHER_PUB_PORT

class _EtherPubSubProxy:
    """Proxy that uses XPUB/XSUB sockets for efficient message distribution.
    
    XPUB/XSUB sockets are special versions of PUB/SUB that expose subscriptions
    as messages, allowing for proper subscription forwarding.
    """
    def __init__(self):
        self.frontend = None
        self.backend = None
        self._running = False
        self.setup_sockets()

    def setup_sockets(self):
        """Setup XPUB/XSUB sockets with optimized settings"""
        self.id = uuid.uuid4()
        self.name = f"EtherPubSubProxy_{self.id}"
        self._logger = logging.getLogger("Proxy")

        self._zmq_context = zmq.Context()
        
        # Use standard ports
        self.frontend = self._zmq_context.socket(zmq.XSUB)
        self.frontend.bind(f"tcp://*:{_ETHER_PUB_PORT}")
        self.frontend.setsockopt(zmq.RCVHWM, 1000000)
        self.frontend.setsockopt(zmq.RCVBUF, 65536)
        
        self.backend = self._zmq_context.socket(zmq.XPUB)
        self.backend.bind(f"tcp://*:{_ETHER_SUB_PORT}")
        self.backend.setsockopt(zmq.SNDHWM, 1000000)
        self.backend.setsockopt(zmq.SNDBUF, 65536)
        self.backend.setsockopt(zmq.XPUB_VERBOSE, 1)
        
        # Set TCP keepalive options
        for socket in [self.frontend, self.backend]:
            socket.setsockopt(zmq.LINGER, 0)
            socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)

        # Create poller to monitor both sockets
        self._poller = zmq.Poller()
        self._poller.register(self.frontend, zmq.POLLIN)
        self._poller.register(self.backend, zmq.POLLIN)
        
        self._logger.info(f"Starting proxy with {self.frontend} and {self.backend}")
    
    def run(self, stop_event: Event):
        """Run the proxy with graceful shutdown support"""
        def handle_signal(signum, frame):
            stop_event.set()
        
        signal.signal(signal.SIGTERM, handle_signal)
        
        try:
            self._running = True
            
            while self._running and not stop_event.is_set():
                try:
                    events = dict(self._poller.poll(timeout=100))  # 100ms timeout
                    
                    if self.frontend in events:
                        message = self.frontend.recv_multipart()
                        self._logger.info(f"Proxy forwarding from frontend: {len(message)} parts")
                        self._logger.info(f"Message: {message}")
                        self.backend.send_multipart(message)
                    
                    if self.backend in events:
                        message = self.backend.recv_multipart()
                        self._logger.info(f"Proxy forwarding from backend: {len(message)} parts")
                        self._logger.info(f"Message: {message}")
                        self.frontend.send_multipart(message)
                        
                except zmq.ZMQError as e:
                    if e.errno == zmq.EAGAIN:  # Timeout, just continue
                        continue
                    else:
                        self._logger.error(f"ZMQ Error in proxy: {e}")
                        raise
                        
        except Exception as e:
            self._logger.error(f"Error in proxy: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        self._running = False
        if self.frontend:
            self.frontend.close()
        if self.backend:
            self.backend.close()
        if self._zmq_context:
            self._zmq_context.term()

    def __del__(self):
        self.cleanup()

class _ProxyManager:
    """Singleton manager for the Ether proxy process"""
    _instance = None
    _proxy_process = None
    _stop_event = None
    _pid_file = os.path.join(tempfile.gettempdir(), 'ether_proxy.pid')
    _parent_pid = None
    _logger = logging.getLogger("ProxyManager")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_ProxyManager, cls).__new__(cls)
        return cls._instance
    
    def start_proxy(self):
        """Start proxy if not already running. Safe to call multiple times."""
        if self._proxy_process is not None:
            return
        
        # Check if proxy is already running on this machine
        self._logger.info(f"PID FILE: {self._pid_file}")
        if os.path.exists(self._pid_file):
            self._logger.info("Already Proxy Running")
            with open(self._pid_file, 'r') as f:
                pid = int(f.read())
                try:
                    os.kill(pid, 0)  # Just check if process exists
                    return  # Proxy is already running
                except OSError:
                    os.remove(self._pid_file)
        
        # Start new proxy process
        self._logger.info("Starting new proxy process")
        self._stop_event = Event()
        self._proxy_process = Process(target=self._run_proxy, args=(self._stop_event,))
        self._proxy_process.daemon = True
        self._proxy_process.start()
        self._parent_pid = os.getpid()
        
        # Save PID
        with open(self._pid_file, 'w') as f:
            f.write(str(self._proxy_process.pid))
    
    def _run_proxy(self, stop_event):
        """Run the proxy process"""
        proxy = _EtherPubSubProxy()
        proxy.run(stop_event)
    
    def stop_proxy(self):
        """Stop proxy if we started it and we're in the creating process"""
        if self._proxy_process is not None and self._parent_pid == os.getpid():
            self._logger.info("Stopping proxy process")
            if self._stop_event is not None:
                self._stop_event.set()
            self._proxy_process.join(timeout=5)
            if self._proxy_process.is_alive():
                self._proxy_process.terminate()
            self._proxy_process = None
            self._stop_event = None
            
            # Force context termination to clear all buffers
            self._logger.info("Terminating ZMQ context")
            zmq.Context.instance().term()
        elif os.path.exists(self._pid_file):
            try:
                with open(self._pid_file, 'r') as f:
                    pid = int(f.read())
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except OSError:
                        pass  # Process might already be gone
                os.remove(self._pid_file)
            except (ValueError, OSError):
                pass  # Ignore errors cleaning up pid file

    def __del__(self):
        self.stop_proxy()

# Create singleton instance
proxy_manager = _ProxyManager()

# Register cleanup on exit
@atexit.register
def _cleanup_proxy():
    proxy_manager.stop_proxy()
```

2. Now let's update `_ether.py` to remove the proxy code and import what we need:

```python:src/ether/_ether.py
# At the top of the file, remove the old proxy classes and add this import:
from ._proxy import proxy_manager

# Remove the _EtherPubSubProxy and _ProxyManager classes and their related code
# The rest of the file remains the same
```

3. Finally, update `__init__.py` to use the new proxy module:

```python:src/ether/__init__.py
from ._proxy import proxy_manager as _proxy_manager
# ... rest of the imports remain the same

# The rest of the file remains the same
```

This refactoring:
1. Creates a new `_proxy.py` file containing all proxy-related code
2. Removes the proxy code from `_ether.py`
3. Updates imports to use the new module
4. Maintains all existing functionality while making the code more organized

The proxy functionality remains exactly the same, but it's now in its own dedicated file which makes the code more maintainable and easier to understand.

---

_**User**_

Great, next, move add_ether_functionaltity from _registry.py to _ether.py

---

_**Assistant**_

I'll help move the `add_ether_functionality` function from `_registry.py` to `_ether.py`. Here are the changes:

```python:src/ether/_ether.py
from functools import wraps
import importlib
from multiprocessing import Event, Process
import inspect
from typing import Any, Set, Type, Optional
import uuid
import zmq
from pydantic import BaseModel, create_model, RootModel
import signal
import logging
import time
import json
import atexit
import os
import tempfile
import sys

from ._registry import EtherRegistry
from ._utils import _get_logger, _ETHER_SUB_PORT, _ETHER_PUB_PORT

def add_ether_functionality(cls):
    """Adds Ether functionality directly to a class"""
    # Collect Ether methods
    ether_methods = {
        name: method for name, method in cls.__dict__.items()
        if hasattr(method, '_pub_metadata') or hasattr(method, '_sub_metadata')
    }
    
    if not ether_methods:
        return cls
    
    # Store Ether method information
    cls._ether_methods_info = ether_methods
    
    # Add core attributes
    def init_ether_vars(self, name=None, log_level=logging.INFO):
        self.id = uuid.uuid4()
        self.name = name or self.id
        self._logger = logging.getLogger(f"{self.__class__.__name__}:{self.name}")
        self._sub_address = f"tcp://localhost:{_ETHER_SUB_PORT}"
        self._pub_address = f"tcp://localhost:{_ETHER_PUB_PORT}"
        
        # Socket handling
        self._zmq_context = zmq.Context()
        self._sub_socket = None
        self._sub_topics = set()
        self._sub_metadata = {}
        self._pub_socket = None
        self._pub_metadata = {}
        
        # Message tracking
        self.received_messages = set()
        self.latencies = []
        self.publishers = {}
        self.first_message_time = None
        self.last_message_time = None
        self.subscription_time = None
        self.results_file = None
    
    def setup_sockets(self):
        self._logger.info("SETUP SOCKETS")
        self._logger.info(f"Setting up sockets for {self.name}")

        # Print initial state
        self._logger.info(f"Initial topics: {self._sub_topics}")
        self._logger.info(f"Initial metadata: {self._sub_metadata}")

        has_sub_method = False
        has_pub_method = False
        for method in self._ether_methods_info.values():
            if hasattr(method, '_sub_metadata'):
                has_sub_method = True
                topic = method._sub_metadata.topic
                self._logger.info(f"Adding sub topic: {topic}")
                self._sub_topics.add(topic)
                self._sub_metadata[topic] = method._sub_metadata
            if hasattr(method, '_pub_metadata'):
                self._logger.info(f'pub to topic {method._pub_metadata.topic}')
                has_pub_method = True

        self._logger.info(f"Final topics: {self._sub_topics}")
        self._logger.info(f"Final metadata: {self._sub_metadata}")

        if hasattr(self, '_sub_address') and has_sub_method:
            self._logger.info("SUB ADDRESS")
            self._sub_socket = self._zmq_context.socket(zmq.SUB)
            if self._sub_address.startswith("tcp://*:"):
                self._sub_socket.bind(self._sub_address)
            else:
                self._sub_socket.connect(self._sub_address)
            self._sub_socket.setsockopt(zmq.RCVHWM, 1000000)
            self._sub_socket.setsockopt(zmq.RCVBUF, 65536)
            self.subscription_time = time.time()
            
            # Setup subscriptions
            for method in self._ether_methods_info.values():
                if hasattr(method, '_sub_metadata'):
                    self._logger.info(f"Subscribing with sub_metadata: {method._sub_metadata}")
                    topic = method._sub_metadata.topic
                    self._sub_socket.subscribe(topic.encode())
                    self._logger.info(f"Subscribed to topic: {topic}")
        
        if hasattr(self, '_pub_address') and has_pub_method:
            self._logger.info("PUB ADDRESS")
            self._pub_socket = self._zmq_context.socket(zmq.PUB)
            if self._pub_address.startswith("tcp://*:"):
                self._pub_socket.bind(self._pub_address)
            else:
                self._pub_socket.connect(self._pub_address)
            self._pub_socket.setsockopt(zmq.SNDHWM, 1000000)
            self._pub_socket.setsockopt(zmq.SNDBUF, 65536)
            self._logger.info("finished pub address if")
        
        time.sleep(0.1)
    
    # Add message tracking
    def track_message(self, publisher_id: str, sequence: int, timestamp: float):
        now = time.time()
        if publisher_id not in self.publishers:
            self.publishers[publisher_id] = {
                "sequences": set(),
                "gaps": [],
                "last_sequence": None,
                "first_time": now
            }
        
        pub_stats = self.publishers[publisher_id]
        if pub_stats["last_sequence"] is not None:
            expected = pub_stats["last_sequence"] + 1
            if sequence > expected:
                gap = sequence - expected
                pub_stats["gaps"].append((expected, sequence, gap))
        
        pub_stats["last_sequence"] = sequence
        pub_stats["sequences"].add(sequence)
        
        latency = (now - timestamp) * 1000
        self.latencies.append(latency)
        self.received_messages.add((publisher_id, sequence))
        
        if self.first_message_time is None:
            self.first_message_time = now
        self.last_message_time = now

    def save_results(self):
        """Save results to file if results_file is set"""
        if not self.results_file:
            return
            
        results = {
            "latencies": self.latencies,
            "received_messages": list(self.received_messages),
            "publishers": {
                pid: {
                    "sequences": list(stats["sequences"]),
                    "gaps": stats["gaps"],
                    "last_sequence": stats["last_sequence"],
                    "first_time": stats["first_time"]
                }
                for pid, stats in self.publishers.items()
            }
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(results, f)

    def receive_single_message(self, timeout=1000):
        if self._sub_socket and self._sub_socket.poll():
            topic = self._sub_socket.recv_string()
            self._logger.info(f"Received raw topic: {topic}")
            self._logger.info(f"Known topics: {self._sub_topics}")
            self._logger.info(f"Known metadata: {self._sub_metadata}")
            
            data = self._sub_socket.recv_json()
            self._logger.info(f"Received data: {data}")
            
            if topic in self._sub_topics:
                self._logger.info(f"Found topic match: {topic}")
                metadata = self._sub_metadata.get(topic)
                if not metadata:
                    self._logger.info(f"No metadata found for topic: {topic}")
                    return
                self._logger.info(f"Found metadata: {metadata}")
                if isinstance(metadata.args_model, type) and issubclass(metadata.args_model, RootModel):
                    args = {'root': metadata.args_model(data).root}
                else:
                    try:
                        model_instance = metadata.args_model(**data)
                        args = model_instance.model_dump()
                    except Exception as e:
                        self._logger.info(f"Error processing data: {e}")
                        raise
                
                metadata.func(self, **args)
            else:
                self._logger.info(f"Received message for unknown topic: {topic}")
    
    # Add run method
    def run(self):
        while True:
            try:
                if self._sub_socket:
                    self.receive_single_message()
            except Exception as e:
                print(f"Error in run loop: {e}")
                break
        
        self.save_results()
        self.cleanup()
    
    # Add cleanup
    def cleanup(self):
        if hasattr(self, '_sub_socket') and self._sub_socket:
            self._sub_socket.close()
        if hasattr(self, '_pub_socket') and self._pub_socket:
            self._pub_socket.close()
        if hasattr(self, '_zmq_context') and self._zmq_context:
            self._zmq_context.term()
    
    # Add methods to class
    cls.init_ether = init_ether_vars
    cls.setup_sockets = setup_sockets
    cls.track_message = track_message
    cls.save_results = save_results
    cls.run = run
    cls.cleanup = cleanup
    cls.receive_single_message = receive_single_message
    
    # Modify __init__ to initialize attributes
    original_init = cls.__init__
    def new_init(self, *args, **kwargs):
        print("NEW INIT")
        self.init_ether(
            name=kwargs.pop('name', None),
            log_level=kwargs.pop('log_level', logging.INFO)
        )
        original_init(self, *args, **kwargs)
        self.setup_sockets()
    cls.__init__ = new_init
    
    # Add cleanup on deletion
    def new_del(self):
        self.cleanup()
    cls.__del__ = new_del
    
    return cls

# Rest of the existing code...
```

```python:src/ether/_registry.py
from typing import Set, Dict, Type
import inspect
import zmq
import sys
import logging
import time
from ._ether import add_ether_functionality

class EtherRegistry:
    """Registry to track and process classes with Ether methods"""
    _pending_classes: Dict[str, str] = {}  # qualname -> module_name
    _processed_classes: Set[str] = set()
    
    @classmethod
    def mark_for_processing(cls, class_qualname: str, module_name: str):
        cls._pending_classes[class_qualname] = module_name
    
    @classmethod
    def process_pending_classes(cls):
        logger = logging.getLogger("EtherRegistry")
        logger.info("Processing pending classes...")
        
        for qualname, module_name in cls._pending_classes.items():
            if qualname in cls._processed_classes:
                logger.debug(f"Class {qualname} already processed, skipping")
                continue
                
            # Import the module that contains the class
            module = sys.modules.get(module_name)
            if module and hasattr(module, qualname):
                class_obj = getattr(module, qualname)
                logger.info(f"Adding Ether functionality to {qualname}")
                add_ether_functionality(class_obj)
                cls._processed_classes.add(qualname)
                logger.info(f"Successfully processed {qualname}")
            else:
                logger.warning(f"Could not find class {qualname} in module {module_name}")
```

The changes:
1. Moved `add_ether_functionality` from `_registry.py` to `_ether.py`
2. Updated `_registry.py` to import `add_ether_functionality` from `_ether`
3. Removed unused imports from `_registry.py`

The functionality remains exactly the same, but the code is now better organized with the core Ether functionality in `_ether.py` and just the registration logic in `_registry.py`.

---



---

