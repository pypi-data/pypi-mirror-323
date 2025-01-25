## SpecStory

## I want to add functionality to be able to do (11/6/2024, 7:21:39 PM)

_**User**_

I want to add functionality to be able to do something like this:

```
from ether import pub

pub({"data": 43}, topic="DataGenerator.generate_data")
```

I'm thinking that EtherInstanceTracker becomes EtherInstanceLiason and keeps it's current functionality but also can publish messages to _PUB_SOCKET via zmq and PUB.

Let me know if there's a better way to intergrate functionality like that, but otherwise let's start moving in this direction.

---

_**Assistant**_

I'll help you add this functionality. The approach of extending EtherInstanceTracker (renamed to EtherInstanceLiaison) makes sense, as it already handles instance management and has Redis connectivity. We'll need to add ZMQ functionality for direct publishing.

Here are the necessary changes:

```python:src/ether/_instance_tracker.py
# Rename file to _instance_liaison.py
import redis
from typing import Optional, Dict, Any, Union
import json
import time
import uuid
import os
import logging
import zmq
from pydantic import BaseModel, RootModel

from ._utils import _ETHER_PUB_PORT

class EtherInstanceLiaison:
    """Manages Ether instances and provides direct message publishing capabilities"""
    _instance = None
    
    def __new__(cls, redis_url: str = "redis://localhost:6379"):
        if cls._instance is None:
            cls._instance = super(EtherInstanceLiaison, cls).__new__(cls)
            cls._instance._init(redis_url)
        return cls._instance
    
    def _init(self, redis_url: str):
        """Initialize the instance (only called once)"""
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.instance_key_prefix = "ether:instance:"
        self._ttl = 60  # seconds until instance considered dead
        self._logger = logging.getLogger("InstanceLiaison")
        
        # Initialize ZMQ context and publisher socket
        self._zmq_context = zmq.Context()
        self._pub_socket = self._zmq_context.socket(zmq.PUB)
        self._pub_socket.connect(f"tcp://localhost:{_ETHER_PUB_PORT}")
        
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        # __new__ handles initialization
        pass
    
    def publish(self, data: Union[Dict, BaseModel], topic: str) -> None:
        """Publish data to a topic
        
        Args:
            data: Data to publish (dict or Pydantic model)
            topic: Topic to publish to
        """
        if not hasattr(self, '_pub_socket'):
            raise RuntimeError("Publisher socket not initialized")
            
        # Convert data to JSON
        if isinstance(data, BaseModel):
            json_data = data.model_dump_json()
        elif isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            raise TypeError("Data must be a dict or Pydantic model")
            
        # Publish message
        self._pub_socket.send_multipart([
            topic.encode(),
            json_data.encode()
        ])
        self._logger.debug(f"Published to {topic}: {json_data}")
    
    def cleanup(self):
        """Cleanup ZMQ resources"""
        if hasattr(self, '_pub_socket'):
            self._pub_socket.close()
        if hasattr(self, '_zmq_context'):
            self._zmq_context.term()
    
    def __del__(self):
        self.cleanup()

    # ... keep all existing instance tracking methods ...
    @property
    def ttl(self) -> int:
        return self._ttl
    
    @ttl.setter
    def ttl(self, value: int):
        self._ttl = value
        for key in self.redis.keys(f"{self.instance_key_prefix}*"):
            self.redis.expire(key, value)
    
    def register_instance(self, instance_id: str, metadata: Dict[str, Any]) -> None:
        key = f"{self.instance_key_prefix}{instance_id}"
        metadata['registered_at'] = time.time()
        metadata['pid'] = os.getpid()
        self.redis.set(key, json.dumps(metadata), ex=self._ttl)
    
    def refresh_instance(self, instance_id: str) -> None:
        key = f"{self.instance_key_prefix}{instance_id}"
        if data := self.redis.get(key):
            self.redis.expire(key, self._ttl)
    
    def deregister_instance(self, instance_id: str) -> None:
        key = f"{self.instance_key_prefix}{instance_id}"
        self.redis.delete(key)
    
    def get_active_instances(self) -> Dict[str, Dict[str, Any]]:
        instances = {}
        for key in self.redis.keys(f"{self.instance_key_prefix}*"):
            if data := self.redis.get(key):
                instance_id = key.replace(self.instance_key_prefix, "")
                instances[instance_id] = json.loads(data)
        return instances
    
    def cleanup_all(self):
        pattern = f"{self.instance_key_prefix}*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def cull_dead_processes(self) -> int:
        removed = 0
        instances = self.get_active_instances()
        
        for instance_id, info in instances.items():
            pid = info.get('pid')
            if pid is None:
                continue
                
            try:
                os.kill(pid, 0)
            except OSError:
                self._logger.info(f"Culling dead instance {instance_id} (PID {pid})")
                self.deregister_instance(instance_id)
                removed += 1
                
        return removed
```

And create a new function in `__init__.py`:

```python:src/ether/__init__.py
# Add to imports
from ._instance_liaison import EtherInstanceLiaison

# Add new function
def pub(data: Union[Dict, BaseModel], topic: str):
    """Publish data to a topic
    
    Args:
        data: Data to publish (dict or Pydantic model)
        topic: Topic to publish to
    """
    liaison = EtherInstanceLiaison()
    liaison.publish(data, topic)

# Update __all__
__all__ = ['ether_pub', 'ether_sub', 'ether_init', 'stop_instance', 'stop_all_instances', 'pub']
```

You'll need to update all imports of `EtherInstanceTracker` to use `EtherInstanceLiaison` instead. The main files that need updating are:

1. `_daemon.py`
2. `_ether.py`
3. Test files

Would you like me to show the necessary changes for those files as well?

This implementation allows you to use the direct publishing functionality as desired:

```python
from ether import pub

# Publish using dict
pub({"data": 43}, topic="DataGenerator.generate_data")

# Or using Pydantic model
from pydantic import BaseModel

class GeneratorData(BaseModel):
    data: int

pub(GeneratorData(data=43), topic="DataGenerator.generate_data")
```

The advantage of this approach is that it:
1. Maintains singleton behavior for ZMQ connections
2. Reuses existing infrastructure
3. Provides type safety through Pydantic support
4. Keeps the instance tracking functionality intact

Would you like me to show the changes needed for the other files?

---

_**User**_



---

_**Assistant**_



---

_**User**_



---

_**Assistant**_

I'll help you modify the `ether_init` function to support quiet mode. We'll need to update both the function signature and the logger initialization logic.

```python:src/ether/__init__.py
# ... existing imports ...

def _init_logger(log_level: int = logging.INFO, quiet: bool = False):
    """Initialize logger with proper cleanup
    
    Args:
        log_level: Logging level to use
        quiet: If True, only log to file, not console
    """
    global _logger
    if _logger is None:
        _logger = _get_logger("EtherMain", log_level=log_level, quiet=quiet)

def ether_init(config: Optional[Union[str, dict, EtherConfig]] = None, 
               force_reinit: bool = False, 
               quiet: bool = False):
    """Initialize the Ether messaging system.
    
    Args:
        config: Optional configuration for instances
        force_reinit: If True, will cleanup and reinitialize even if already initialized
        quiet: If True, loggers will only write to file, not console
    """
    global _ether_initialized, _instance_processes
    
    if _ether_initialized and force_reinit:
        # Clean up existing system
        _init_logger(quiet=quiet)
        _logger.debug("Force reinitializing Ether system...")
        _cleanup_handler()
        _ether_initialized = False
        
    if not _ether_initialized:
        # Initialize logger
        _init_logger(quiet=quiet)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, _cleanup_handler)
        signal.signal(signal.SIGTERM, _cleanup_handler)
        
        # Clean up any existing ZMQ contexts
        zmq.Context.instance().term()
        
        # Start daemon (which manages Redis and PubSub)
        daemon_manager.start(quiet=quiet)  # Pass quiet mode to daemon
        
        # ... rest of the function remains the same ...
```

We'll also need to update the `_get_logger` utility function to support quiet mode:

```python:src/ether/_utils.py
def _get_logger(process_name: str = "Ether", 
                instance_name: Optional[str] = None,
                log_level: int = logging.INFO,
                quiet: bool = False) -> logging.Logger:
    """Get a logger with proper configuration
    
    Args:
        process_name: Name of the process for logging
        instance_name: Optional instance name for more specific logging
        log_level: Logging level to use
        quiet: If True, only log to file, not console
    """
    # Create logger name
    logger_name = process_name
    if instance_name:
        logger_name = f"{process_name}.{instance_name}"
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Always set up file logging
    if instance_name:
        log_dir = _INSTANCES_LOG_DIR / process_name
    else:
        log_dir = _DAEMON_LOG_DIR if process_name == "EtherDaemon" else _LOG_DIR
    
    _ensure_log_dir(log_dir)
    file_handler = logging.FileHandler(
        log_dir / f"{logger_name}.log"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add console handler only if not in quiet mode
    if not quiet:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger
```

And finally, update the daemon manager to support quiet mode:

```python:src/ether/_daemon.py
class _EtherDaemon:
    """Manages Redis and PubSub services for Ether"""
    # ... existing code ...
    
    def start(self, quiet: bool = False):
        """Start all daemon services
        
        Args:
            quiet: If True, loggers will only write to file
        """
        if self._started:
            return
        
        # Update logger for quiet mode
        self._logger = _get_logger("EtherDaemon", log_level=logging.INFO, quiet=quiet)
        
        # Start services
        self._ensure_redis_running()
        self._ensure_pubsub_running(quiet)
        
        # Start monitoring in separate process
        self._monitor_process = Process(target=_run_monitor, args=(quiet,))
        self._monitor_process.daemon = True
        self._monitor_process.start()
        
        self._started = True

def _run_monitor(quiet: bool = False):
    """Standalone function to run instance monitoring
    
    Args:
        quiet: If True, logger will only write to file
    """
    logger = _get_logger("EtherMonitor", log_level=logging.INFO, quiet=quiet)
    tracker = EtherInstanceLiaison()
    
    while True:
        try:
            # Cull dead processes first
            culled = tracker.cull_dead_processes()
            if culled:
                logger.debug(f"Culled {culled} dead instances")
            
            # Get remaining active instances
            instances = tracker.get_active_instances()
            logger.debug(f"Active instances: {instances}")
            time.sleep(CULL_INTERVAL)  # Check every CULL_INTERVAL seconds
        except Exception as e:
            logger.error(f"Error monitoring instances: {e}")
            time.sleep(1)
```

These changes will:
1. Add a `quiet` parameter to `ether_init`
2. Modify the logger initialization to support quiet mode
3. Propagate quiet mode settings through the daemon and monitoring processes
4. Ensure all loggers still write to files even in quiet mode

When quiet mode is enabled, all logging output will be written to files in the appropriate directories but won't appear in the console. This can be useful for running in production environments or when you want to reduce console output.

Usage example:
```python
from ether import ether_init

# Initialize with quiet mode (logs only to files)
ether_init(quiet=True)

# Or with normal logging (console and files)
ether_init(quiet=False)  # default behavior
```

---

_**User**_

When run benchmark.py with more than one paramater setting, i.e. the lists for message length, num messages, num subscribers, num publishers are not all length one, then we no longer save the files. I can see that the logger doesn't print anything the second time inside of BenchmarkSubsriber.save_results()

---

_**Assistant**_

Looking at the code, I can see the issue. The problem is that the `results_file` attribute isn't being properly initialized in subsequent runs because the `_logger` is being accessed before the instance is fully initialized. Let's fix the `BenchmarkSubscriber` class:

```python:src/scripts/benchmark.py
class BenchmarkSubscriber:
    """Subscriber that receives messages and tracks statistics."""
    def __init__(self, results_dir: str = None, subscriber_id: int = 0, name: str = None):
        # Initialize basic attributes first
        self.subscriber_id = subscriber_id
        self.results_file = None
        self.received_messages = []
        self.latencies = []
        self.publishers = {}
        
        # Set results file if directory provided
        if results_dir:
            self.results_file = os.path.join(results_dir, f"subscriber_{subscriber_id}.json")
            # Only log after instance is properly initialized with _logger
            if hasattr(self, '_logger'):
                self._logger.debug(f"Results file set to: {self.results_file}")
    
    @ether_sub()
    def receive_message(self, data: str, timestamp: float, message_id: int, 
                       publisher_id: str, sequence: int):
        """Track received message statistics"""
        now = time.time()
        latency = (now - timestamp) * 1000  # Convert to ms
        self.latencies.append(latency)
        self.received_messages.append((publisher_id, sequence))
        
        if publisher_id not in self.publishers:
            self.publishers[publisher_id] = {
                "sequences": set(),
                "gaps": [],
                "last_sequence": None
            }
        
        pub_stats = self.publishers[publisher_id]
        if pub_stats["last_sequence"] is not None:
            expected = pub_stats["last_sequence"] + 1
            if sequence > expected:
                gap = sequence - expected
                pub_stats["gaps"].append((expected, sequence, gap))
        
        pub_stats["last_sequence"] = sequence
        pub_stats["sequences"].add(sequence)
    
    @ether_save()
    def save_results(self):
        """Save results to file"""
        if not self.results_file:  # Changed from hasattr check to direct attribute check
            self._logger.warning("No results file path set")
            return
            
        results = {
            "latencies": self.latencies,
            "received_messages": self.received_messages,
            "publishers": {
                pid: {
                    "sequences": list(stats["sequences"]),
                    "gaps": stats["gaps"],
                    "last_sequence": stats["last_sequence"]
                }
                for pid, stats in self.publishers.items()
            }
        }
        
        self._logger.info(f"Saving results to {self.results_file}")
        with open(self.results_file, 'w') as f:
            json.dump(results, f)
```

The changes made:
1. Initialize `results_file` to None by default
2. Move the logger debug message after instance initialization
3. Change the `hasattr` check to a direct attribute check in `save_results`
4. Add warning log when no results file is set
5. Add `name` parameter to `__init__` to match the config being passed

This should fix the issue with results not being saved in subsequent runs. The problem was that the `_logger` was being accessed during initialization before Ether had a chance to properly set it up, which could cause the `results_file` attribute to not be set properly.

Would you like me to show any other changes or explain the fix in more detail?

---

_**User**_

We dont' seem to be getting insdie of BenchmarkSubscriber.save_results... why?

---

_**Assistant**_

If the `BenchmarkSubscriber.save_results` method is not being called, there are a few potential reasons to investigate:

1. **Decorator Issue**: Ensure that the `@ether_save()` decorator is correctly set up to trigger the `save_results` method. If the decorator is not functioning as expected, the method may not be called.

2. **Method Invocation**: Verify that the `save_results` method is being explicitly called somewhere in your code. If it's intended to be called automatically, ensure that the mechanism for triggering it is working correctly.

3. **Logging**: Add logging statements at the start of the `save_results` method to confirm whether it's being entered. This can help determine if the method is being called but failing silently.

4. **Error Handling**: Check if there are any exceptions being raised within the `save_results` method that might prevent it from completing. These could be caught and logged to provide more insight.

5. **Configuration**: Ensure that the `BenchmarkSubscriber` instances are being properly configured with a `results_file` path. If this is not set, the method might exit early.

Here's a modified version of the `save_results` method with additional logging to help diagnose the issue:

```python:src/scripts/benchmark.py
class BenchmarkSubscriber:
    # ... existing code ...

    @ether_save()
    def save_results(self):
        """Save results to file"""
        if not self.results_file:
            self._logger.warning("No results file path set")
            return
        
        self._logger.info("Entering save_results method")
        
        try:
            results = {
                "latencies": self.latencies,
                "received_messages": self.received_messages,
                "publishers": {
                    pid: {
                        "sequences": list(stats["sequences"]),
                        "gaps": stats["gaps"],
                        "last_sequence": stats["last_sequence"]
                    }
                    for pid, stats in self.publishers.items()
                }
            }
            
            self._logger.info(f"Saving results to {self.results_file}")
            with open(self.results_file, 'w') as f:
                json.dump(results, f)
        except Exception as e:
            self._logger.error(f"Error saving results: {e}")
```

Make sure that the logger is properly initialized and that the logging level is set to capture info and error messages. This will help you determine if the method is being called and if any errors are occurring during execution.

---

_**User**_

Why would it be that only the first call to `run_benchmark` gets inside `BenchmarkSubscriber.save_results`?

---

_**Assistant**_

The issue where only the first call to `run_benchmark` gets inside `BenchmarkSubscriber.save_results` could be due to several reasons. Here are some potential causes and solutions:

1. **Singleton or Global State**: If the `Ether` system or any of its components (like `EtherInstanceLiaison`) is maintaining a global or singleton state, it might not be properly resetting between benchmark runs. Ensure that any global state is reset or reinitialized between runs.

2. **Instance Reuse**: If the `BenchmarkSubscriber` instances are being reused across different benchmark runs without proper reinitialization, they might not be set up correctly for subsequent runs. Ensure that each run of `run_benchmark` creates fresh instances of `BenchmarkSubscriber`.

3. **Results File Overwriting**: If the results files are being overwritten or not properly set for each subscriber, the `save_results` method might not be called because the file path is not set. Ensure that each `BenchmarkSubscriber` has a unique `results_file` path for each run.

4. **Logging Configuration**: If the logger is not properly configured or if logging is disabled after the first run, you might not see the log messages. Ensure that logging is correctly set up for each run.

5. **Ether System Initialization**: If the `ether_init` function is not properly reinitializing the system between runs, it might not trigger the necessary setup for the `save_results` method to be called. Ensure that `ether_init` is called with `force_reinit=True` and that it properly resets the system.

6. **Decorator Behavior**: The `@ether_save()` decorator might have specific behavior that prevents it from being triggered more than once. Check the implementation of this decorator to ensure it supports multiple invocations.

To help diagnose the issue, you can add logging statements at key points in the code to track the flow of execution and ensure that each component is being properly initialized and called. Here's an example of how you might add logging to the `run_benchmark` function:

```python:src/scripts/benchmark.py
def run_benchmark(message_size: int, num_messages: int, num_subscribers: int, num_publishers: int) -> BenchmarkResult:
    """Run a single benchmark configuration"""
    logging.info(f"Running benchmark with {num_publishers} publishers and {num_subscribers} subscribers")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration for subscribers
        config = {
            "instances": {
                f"benchmark_subscriber_{i}": {
                    "class_path": "scripts.benchmark.BenchmarkSubscriber",
                    "kwargs": {
                        "results_dir": temp_dir,
                        "subscriber_id": i,
                        "name": f"benchmark_subscriber_{i}"
                    },
                } for i in range(num_subscribers)
            }
        }
        
        # Initialize Ether system with configuration
        ether_init(
            config=config, 
            force_reinit=True
        )
        
        # Create publishers (these we'll manage manually)
        publishers = []
        for i in range(num_publishers):
            publisher = BenchmarkPublisher(message_size)
            publishers.append(publisher)
        
        # Allow time for connections to establish
        time.sleep(1.0)
        
        # Start actual benchmark
        start_time = time.time()
        
        messages_per_publisher = num_messages
        total_messages_sent = 0
        message_interval = 0.0001 * (num_subscribers / 2)
        
        for publisher in publishers:
            for _ in range(messages_per_publisher):
                publisher.publish_message(time.time())
                total_messages_sent += 1
                time.sleep(message_interval)
        
        logging.info("Calling Ether.save()")
        Ether.save()

        end_time = time.time()
        duration = end_time - start_time
        
        # Allow time for final messages to be processed
        time.sleep(1.0)
        
        # Collect and process results
        all_latencies = []
        subscriber_results = []
        
        for i in range(num_subscribers):
            result_file = os.path.join(temp_dir, f"subscriber_{i}.json")
            try:
                with open(result_file, 'r') as f:
                    results = json.load(f)
                    all_latencies.extend(results["latencies"])
                    subscriber_results.append(results)
            except FileNotFoundError:
                logging.warning(f"Could not find results file for subscriber {i}")
                continue
        
        # Calculate metrics
        total_messages_sent = num_messages * num_publishers
        expected_per_sub = total_messages_sent
        total_expected = expected_per_sub * num_subscribers
        
        total_received = sum(len(results["received_messages"]) for results in subscriber_results)
        message_loss_percent = 100 * (1 - total_received / total_expected)
        
        return BenchmarkResult(
            messages_per_second=total_messages_sent / duration if duration > 0 else 0,
            latency_ms=statistics.mean(all_latencies) if all_latencies else 0,
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            message_loss_percent=message_loss_percent,
            messages_sent=total_messages_sent,
            expected_sent=total_messages_sent,
            messages_received=total_received,
            expected_received=total_expected
        )
```

By adding logging, you can track whether the `Ether.save()` call is being made and whether the results files are being created and accessed correctly. This can help identify where the process is breaking down.

---

_**User**_

Hmm... here's the output:


---

_**Assistant**_

The issue where only the first call to `run_benchmark` successfully saves results, while subsequent calls do not, could be due to several factors. Based on the output and the code, here are some potential causes and solutions:

1. **Resource Cleanup**: Ensure that resources are properly cleaned up between benchmark runs. The `Ether` system might not be fully resetting, leading to issues in subsequent runs. The `ether_init` function should be called with `force_reinit=True` to ensure a clean state.

2. **Temporary Directory**: The temporary directory used for storing results might be getting cleaned up or not properly set for subsequent runs. Ensure that each run of `run_benchmark` creates a new temporary directory and that the `results_file` paths are correctly set for each `BenchmarkSubscriber`.

3. **Instance Reinitialization**: Make sure that each `BenchmarkSubscriber` is properly reinitialized for each benchmark run. If instances are being reused without proper reinitialization, they might not function correctly.

4. **Logging and Debugging**: Add more logging to track the flow of execution and ensure that all components are being initialized and called as expected. This can help identify where the process is breaking down.

5. **Ether System State**: The `Ether` system might be maintaining state between runs that is not being reset. Ensure that all components, including the `EtherInstanceLiaison` and any global state, are properly reset between runs.

Here's a potential modification to ensure proper cleanup and reinitialization:

```python:src/scripts/benchmark.py
def run_benchmark(message_size: int, num_messages: int, num_subscribers: int, num_publishers: int) -> BenchmarkResult:
    """Run a single benchmark configuration"""
    logging.info(f"Running benchmark with {num_publishers} publishers and {num_subscribers} subscribers")
    
    # Use a new temporary directory for each run
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration for subscribers
        config = {
            "instances": {
                f"benchmark_subscriber_{i}": {
                    "class_path": "scripts.benchmark.BenchmarkSubscriber",
                    "kwargs": {
                        "results_dir": temp_dir,
                        "subscriber_id": i,
                        "name": f"benchmark_subscriber_{i}"
                    },
                } for i in range(num_subscribers)
            }
        }
        
        # Initialize Ether system with configuration
        ether_init(
            config=config, 
            force_reinit=True  # Ensure clean state
        )
        
        # Create publishers (these we'll manage manually)
        publishers = []
        for i in range(num_publishers):
            publisher = BenchmarkPublisher(message_size)
            publishers.append(publisher)
        
        # Allow time for connections to establish
        time.sleep(1.0)
        
        # Monitor resources
        process = psutil.Process(os.getpid())
        
        # Start actual benchmark
        start_time = time.time()
        
        messages_per_publisher = num_messages
        total_messages_sent = 0
        message_interval = 0.0001 * (num_subscribers / 2)
        
        for publisher in publishers:
            for _ in range(messages_per_publisher):
                publisher.publish_message(time.time())
                total_messages_sent += 1
                time.sleep(message_interval)
        
        logging.info("Calling Ether.save()")
        Ether.save()

        end_time = time.time()
        duration = end_time - start_time
        
        # Allow time for final messages to be processed
        time.sleep(1.0)
        
        # Collect and process results
        all_latencies = []
        subscriber_results = []
        
        for i in range(num_subscribers):
            result_file = os.path.join(temp_dir, f"subscriber_{i}.json")
            try:
                with open(result_file, 'r') as f:
                    results = json.load(f)
                    all_latencies.extend(results["latencies"])
                    subscriber_results.append(results)
            except FileNotFoundError:
                logging.warning(f"Could not find results file for subscriber {i}")
                continue
        
        # Calculate metrics
        total_messages_sent = num_messages * num_publishers
        expected_per_sub = total_messages_sent
        total_expected = expected_per_sub * num_subscribers
        
        total_received = sum(len(results["received_messages"]) for results in subscriber_results)
        message_loss_percent = 100 * (1 - total_received / total_expected)
        
        return BenchmarkResult(
            messages_per_second=total_messages_sent / duration if duration > 0 else 0,
            latency_ms=statistics.mean(all_latencies) if all_latencies else 0,
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            message_loss_percent=message_loss_percent,
            messages_sent=total_messages_sent,
            expected_sent=total_messages_sent,
            messages_received=total_received,
            expected_received=total_expected
        )
```

This modification ensures that each benchmark run uses a new temporary directory and that the `Ether` system is fully reinitialized. Additionally, ensure that the `Ether.save()` call is correctly triggering the `save_results` method for each `BenchmarkSubscriber

---



---

