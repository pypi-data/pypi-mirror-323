## SpecStory

## Managing Network Configuration in Ether (1/19/2025, 11:28:27 PM)

_**User**_

So far we've only passed messages locally within a computer. So across process but using `localhost`. We use localhost in four different files in @_internal . We should use an IP address that is set in `EtherConfig` whose default is `localhost`.

One important question though is how we can make these values in the config available to the other classes and stuff. We could propagate those values, but is there a way where some config can be available?

One idea I have is to store it in the EtherSession metadata so it returns with Ether.get_current_session().

---

_**Assistant**_

That's a good approach! We can store network configuration in the EtherSession metadata and make it available through `get_current_session()`. This way, all components can access the network settings without needing to pass them around explicitly.

Let's modify the config and session files first:

```python:src/ether/_internal/_config.py
# Add new NetworkConfig class
class NetworkConfig(BaseModel):
    """Network configuration for Ether"""
    host: str = "localhost"
    pubsub_frontend_port: int = 5555
    pubsub_backend_port: int = 5556
    reqrep_frontend_port: int = 5559
    reqrep_backend_port: int = 5560
    redis_port: int = 6379
    session_discovery_port: int = 301309
    session_query_port: int = 301310

class EtherConfig(BaseModel):
    """Complete Ether configuration"""
    registry: Dict[str, EtherClassConfig] = Field(default_factory=dict)
    instances: Dict[str, EtherInstanceConfig] = Field(default_factory=dict)
    network: NetworkConfig = Field(default_factory=NetworkConfig)  # Add network config
    
    @classmethod
    def from_yaml(cls, path: str) -> "EtherConfig":
        """Load configuration from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
```

Now let's modify the session to store network config:

```python:src/ether/_internal/_session.py
# Update EtherSession.__init__
def __init__(self, ether_id: str = "default", network_config: Optional[NetworkConfig] = None):
    self.session_id = str(uuid.uuid4())
    self.ether_id = ether_id
    self.context = zmq.Context()
    self.is_discovery_service = False
    self.running = False
    self._logger = get_ether_logger(process_name="EtherSession")
    
    # Use provided network config or defaults
    self.network = network_config or NetworkConfig()
    
    self.metadata = {
        "session_id": self.session_id,
        "ether_id": ether_id,
        "start_time": time.time(),
        "pid": os.getpid(),
        "network": self.network.model_dump()  # Add network config to metadata
    }
    
    try:
        if not self._connect_to_discovery():
            self._logger.debug(f"Process {os.getpid()}: No existing service found, attempting to start one...")
            self._start_discovery_service()
    except Exception as e:
        self.cleanup()
        raise e

    atexit.register(self.cleanup)

# Update discovery service ports to use network config
def _start_discovery_service(self):
    try:
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://*:{self.network.session_discovery_port}")
        
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind(f"tcp://*:{self.network.session_query_port}")
        # ... rest of method unchanged
```

Then in `_ether.py`, we can update the start method to pass network config to the session:

```python:src/ether/_internal/_ether.py
def start(self, ether_id: str, config = None, restart: bool = False):
    """Start all daemon services"""
    self._logger.debug(f"Start called with ether_id={ether_id}, config={config}, restart={restart}")
    self._ether_id = ether_id

    # Process configuration
    if config:
        if isinstance(config, (str, dict)):
            config = EtherConfig.from_yaml(config) if isinstance(config, str) else EtherConfig.model_validate(config)
        network_config = config.network
    else:
        network_config = NetworkConfig()

    # Start session with network config
    self._ether_session_process = Process(
        target=session_process_launcher, 
        args=(self._ether_id, network_config)
    )
    self._ether_session_process.start()
    time.sleep(1.0)

    # ... rest of method unchanged
```

Now any component can get the network configuration by checking the session metadata:

```python
session_data = EtherSession.get_current_session()
if session_data:
    network_config = NetworkConfig.model_validate(session_data["network"])
    host = network_config.host
    pubsub_port = network_config.pubsub_frontend_port
    # etc...
```

Would you like me to show the changes needed for the other components (PubSub proxy, ReqRep broker, etc.) to use these network settings? The basic pattern would be to get the network config from the session metadata when initializing each component.

This approach has several benefits:
1. Configuration is centralized in one place
2. Components can access network settings without direct dependencies
3. Settings are consistent across all components
4. Default values make it optional
5. Network config can be changed via YAML config files

Let me know if you'd like to see the changes for the other components or if you have any questions about this approach!

---

_**User**_

Ok great. Let's use `EtherSession` to get these values in @liaison.py 

---

_**Assistant**_

I'll help modify the `EtherInstanceLiaison` class to get network configuration from the session metadata. Here's how we can update it:

```python:src/ether/liaison.py
import redis
from typing import Dict, Any
import json
import time
import os

from ether.utils import get_ether_logger
from ether._internal._session import EtherSession
from ether._internal._config import NetworkConfig

class EtherInstanceLiaison:
    """An interface for (de)registrations and process tracking for instances"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EtherInstanceLiaison, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """Initialize the instance (only called once)"""
        self._logger = get_ether_logger("EtherInstanceLiaison")
        
        # Get network config from session
        session_data = EtherSession.get_current_session()
        if session_data and "network" in session_data:
            network_config = NetworkConfig.model_validate(session_data["network"])
            self._logger.debug(f"Using network config from session: {network_config}")
        else:
            network_config = NetworkConfig()
            self._logger.debug("No session found, using default network config")
            
        # Connect to Redis using network config
        redis_url = f"redis://{network_config.host}:{network_config.redis_port}"
        self._logger.debug(f"Connecting to Redis at {redis_url}")
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        
        self.instance_key_prefix = "ether:instance:"
        self._ttl = 60  # seconds until instance considered dead
    
    def __init__(self):
        # __new__ handles initialization
        pass
    
    # Rest of the class remains unchanged...
```

Key changes:
1. Removed the `redis_url` parameter since we'll get it from session config
2. Added imports for `EtherSession` and `NetworkConfig`
3. Modified `_init` to get network config from session metadata
4. Updated Redis connection to use the configured host and port

The liaison will now automatically use the network configuration from the session, falling back to defaults if no session is found. This maintains compatibility while allowing for network configuration.

Would you like me to show how to update the other components (PubSub proxy, ReqRep broker) to use the network configuration as well?

---

_**User**_

We need to update `session_process_launcher` to take the config

---

_**Assistant**_

Yes, let's update the `session_process_launcher` function to accept the network config parameter:

```python:src/ether/_internal/_session.py
def session_process_launcher(process_id: str, network_config: Optional[NetworkConfig] = None):
    """Launch an Ether session process
    
    Args:
        process_id: ID for the process/session
        network_config: Optional network configuration
    """
    try:
        # First try to find existing session
        current_session = EtherSession.get_current_session(timeout=200)
        
        if current_session is None:
            try:
                session_mgr = EtherSession(
                    ether_id=process_id,
                    network_config=network_config
                )
                while True:
                    time.sleep(1.0)
            except zmq.ZMQError as e:
                if e.errno == errno.EADDRINUSE:
                    # Someone else created it just before us, try to get their session
                    current_session = EtherSession.get_current_session(timeout=200)
                else:
                    raise
        else:
            pass
            
    except Exception as e:
        pass
    finally:
        pass
```

This change:
1. Adds the `network_config` parameter with type hint
2. Passes the network config when creating a new session
3. Maintains backwards compatibility with the optional parameter

The network configuration will now flow from the main Ether instance through the session process and be available in the session metadata for other components to use.

Would you like me to show how to update the other components that need to use this network configuration?

---

_**User**_

Ok. I made some of the updates. Next let's send the host and necessary port values from inside this method through to the creation of the pub sub proxy:


---

_**Assistant**_

I'll help update the PubSub proxy initialization to use the network configuration. First, let's modify the `_run_pubsub` function in `_ether.py` to receive and pass the network config:

```python:src/ether/_internal/_ether.py
def _run_pubsub(network_config: Optional[NetworkConfig] = None):
    """Standalone function to run PubSub proxy
    
    Args:
        network_config: Network configuration for the proxy
    """
    # Get network config from session if not provided
    if network_config is None:
        session_data = EtherSession.get_current_session()
        if session_data and "network" in session_data:
            network_config = NetworkConfig.model_validate(session_data["network"])
        else:
            network_config = NetworkConfig()
    
    proxy = _EtherPubSubProxy(network_config=network_config)
    
    def handle_stop(signum, frame):
        """Handle stop signal by cleaning up proxy"""
        proxy._logger.debug("Received stop signal, shutting down proxy...")
        proxy.cleanup()
        os._exit(0)  # Exit cleanly
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    
    proxy.run()

# Update the ensure method to pass network config
def _ensure_pubsub_running(self) -> bool:
    """Ensure PubSub proxy is running"""
    # Clean up any existing ZMQ contexts
    zmq.Context.instance().term()
    if self._pubsub_process is None:
        self._pubsub_process = Process(
            target=_run_pubsub,
            args=(self._config.network,)
        )
        self._pubsub_process.daemon = True
        self._pubsub_process.start()

    return self._test_pubsub_connection()
```

Then update the PubSub proxy class to use the network config:

```python:src/ether/_internal/_pubsub.py
class _EtherPubSubProxy:
    """Proxy that uses XPUB/XSUB sockets for efficient message distribution."""
    
    def __init__(self, network_config: Optional[NetworkConfig] = None):
        self.id = uuid.uuid4()
        self.name = f"EtherPubSubProxy_{self.id}"
        self._logger = get_ether_logger("EtherPubSubProxy")
        self._logger.debug("Initializing PubSub proxy")
        
        # Use provided network config or get from session
        if network_config is None:
            session_data = EtherSession.get_current_session()
            if session_data and "network" in session_data:
                network_config = NetworkConfig.model_validate(session_data["network"])
            else:
                network_config = NetworkConfig()
        self.network = network_config
        
        self.capture_socket = None
        self.broadcast_socket = None
        self._running = False
        self.setup_sockets()

    def setup_sockets(self):
        """Setup XPUB/XSUB sockets with optimized settings"""
        self._logger.debug("Setting up ZMQ sockets")
        
        self._zmq_context = zmq.Context()
        
        # Setup capture (XSUB) socket
        self._logger.debug(f"Setting up XSUB socket on port {self.network.pubsub_backend_port}")
        self.capture_socket = self._zmq_context.socket(zmq.XSUB)
        self.capture_socket.bind(f"tcp://{self.network.host}:{self.network.pubsub_backend_port}")
        self.capture_socket.setsockopt(zmq.RCVHWM, 1000000)
        self.capture_socket.setsockopt(zmq.RCVBUF, 65536)
        
        # Setup broadcast (XPUB) socket
        self._logger.debug(f"Setting up XPUB socket on port {self.network.pubsub_frontend_port}")
        self.broadcast_socket = self._zmq_context.socket(zmq.XPUB)
        self.broadcast_socket.bind(f"tcp://{self.network.host}:{self.network.pubsub_frontend_port}")
        self.broadcast_socket.setsockopt(zmq.SNDHWM, 1000000)
        self.broadcast_socket.setsockopt(zmq.SNDBUF, 65536)
        self.broadcast_socket.setsockopt(zmq.XPUB_VERBOSE, 1)
        
        # Rest of method unchanged...
```

These changes:
1. Add network_config parameter to `_run_pubsub`
2. Pass network config from `_ensure_pubsub_running` 
3. Update PubSub proxy to use network config for socket bindings
4. Add fallback to session metadata if no config provided
5. Use configured host and ports throughout

Would you like me to show the changes for the ReqRep broker as well?

---



---

