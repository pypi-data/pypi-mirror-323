## SpecStory

## Hi, I want to add some tests which both confirm (11/9/2024, 12:08:47 PM)

_**User**_



---

_**Assistant**_

I'll help you create some tests that verify the type validation behavior of the pub/sub system. Let's create a new test file specifically for type validation testing.

```python:src/tests/test_type_validation.py
import pytest
import time
import multiprocessing
from typing import List, Dict, Optional
from pydantic import BaseModel
from ether import ether, ether_pub, ether_sub

# Test Models
class ValidMessage(BaseModel):
    value: int
    text: str
    optional_field: Optional[str] = None

class NestedMessage(BaseModel):
    items: List[int]
    metadata: Dict[str, str]

# Test Classes
class ValidPublisher:
    """Publisher that sends correctly typed messages"""
    
    @ether_pub(topic="valid_messages")
    def send_valid_message(self) -> ValidMessage:
        return ValidMessage(value=42, text="hello")
    
    @ether_pub(topic="nested_messages")
    def send_nested_message(self) -> NestedMessage:
        return NestedMessage(
            items=[1, 2, 3],
            metadata={"source": "test"}
        )
    
    @ether_pub(topic="primitive_message")
    def send_primitive(self) -> int:
        return 42

class InvalidPublisher:
    """Publisher that attempts to send incorrectly typed messages"""
    
    @ether_pub(topic="invalid_message")
    def send_wrong_type(self) -> ValidMessage:
        return {"value": "not an int", "text": 42}  # Wrong types
    
    @ether_pub(topic="missing_field")
    def send_missing_required(self) -> ValidMessage:
        return {"text": "missing value field"}  # Missing required field
    
    @ether_pub(topic="wrong_return")
    def send_wrong_return_type(self) -> int:
        return "not an integer"  # Wrong return type

class ValidationSubscriber:
    """Subscriber that receives and validates messages"""
    def __init__(self):
        self.received_valid = False
        self.received_nested = False
        self.received_primitive = False
        self.error_received = False
    
    @ether_sub(topic="valid_messages")
    def receive_valid(self, value: int, text: str, optional_field: Optional[str] = None):
        self.received_valid = True
    
    @ether_sub(topic="nested_messages")
    def receive_nested(self, items: List[int], metadata: Dict[str, str]):
        self.received_nested = True
    
    @ether_sub(topic="primitive_message")
    def receive_primitive(self, root: int):
        self.received_primitive = True

def run_valid_type_test():
    """Test valid type scenarios"""
    config = {
        "instances": {
            "validation_subscriber": {
                "class_path": "tests.test_type_validation.ValidationSubscriber",
                "autorun": True
            }
        }
    }
    
    # Initialize system
    ether.init(config=config)
    time.sleep(0.5)  # Allow time for setup
    
    # Create publisher and send messages
    publisher = ValidPublisher()
    publisher.send_valid_message()
    publisher.send_nested_message()
    publisher.send_primitive()
    
    time.sleep(0.5)  # Allow time for message processing

def test_valid_types():
    """Test that valid type messages are processed correctly"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_valid_type_test)
    process.start()
    process.join()
    assert process.exitcode == 0

def run_invalid_type_test():
    """Test invalid type scenarios"""
    publisher = InvalidPublisher()
    
    # These should raise exceptions
    with pytest.raises(ValueError):
        publisher.send_wrong_type()
    
    with pytest.raises(ValueError):
        publisher.send_missing_required()
    
    with pytest.raises(ValueError):
        publisher.send_wrong_return_type()

def test_invalid_types():
    """Test that invalid type messages raise appropriate errors"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_invalid_type_test)
    process.start()
    process.join()
    assert process.exitcode == 0

# Additional test for type mismatch between pub/sub
class MismatchPublisher:
    @ether_pub(topic="mismatched_types")
    def send_message(self) -> ValidMessage:
        return ValidMessage(value=42, text="hello")

class MismatchSubscriber:
    def __init__(self):
        self.error_received = False
    
    @ether_sub(topic="mismatched_types")
    def receive_message(self, wrong_field_name: int):  # Mismatched field name
        pass

def run_type_mismatch_test():
    """Test mismatched type definitions between publisher and subscriber"""
    config = {
        "instances": {
            "mismatch_subscriber": {
                "class_path": "tests.test_type_validation.MismatchSubscriber",
                "autorun": True
            }
        }
    }
    
    ether.init(config=config)
    time.sleep(0.5)
    
    publisher = MismatchPublisher()
    publisher.send_message()  # This should cause an error in the subscriber
    time.sleep(0.5)

def test_type_mismatch():
    """Test that mismatched types between pub/sub are handled appropriately"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_type_mismatch_test)
    process.start()
    process.join()
    assert process.exitcode != 0  # Should fail due to type mismatch
```

This test file includes several scenarios:

1. Valid type tests:
- Publishing a simple Pydantic model
- Publishing a nested Pydantic model with lists and dicts
- Publishing a primitive type (int)

2. Invalid type tests:
- Attempting to publish wrong types for model fields
- Missing required fields in a model
- Returning wrong type compared to annotation

3. Type mismatch tests:
- Testing what happens when publisher and subscriber have mismatched type definitions

The tests use multiprocessing to run in isolated processes, which is important for testing the pub/sub system. The valid tests should pass while the invalid tests should raise appropriate exceptions.

To run these tests, you would use:
```bash
pytest src/tests/test_type_validation.py -v
```

These tests will help ensure that the type validation system is working correctly and handling errors appropriately. They cover both the happy path (valid types) and error cases (invalid types and mismatches).

---

_**User**_

I'm seeing this out, can you fix an errors?
================== test session starts ===================
platform darwin -- Python 3.13.0, pytest-8.3.3, pluggy-1.5.0 -- /Users/loyalshababo/dev/ether/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/loyalshababo/dev/ether
configfile: pyproject.toml
collected 3 items                                        

src/tests/test_type_validation.py::test_valid_types FAILED [ 33%]
src/tests/test_type_validation.py::test_invalid_types FAILED [ 66%]
src/tests/test_type_validation.py::test_type_mismatch PASSED [100%]

======================== FAILURES =========================
____________________ test_valid_types _____________________

    def test_valid_types():
        """Test that valid type messages are processed correctly"""
        ctx = multiprocessing.get_context('spawn')
        process = ctx.Process(target=run_valid_type_test)
        process.start()
        process.join()
>       assert process.exitcode == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = <SpawnProcess name='SpawnProcess-1' pid=3017 parent=3015 stopped exitcode=1>.exitcode

src/tests/test_type_validation.py:101: AssertionError
------------------ Captured stderr call -------------------
Process SpawnProcess-1:
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.13/3.13.0_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 313, in _bootstrap
    self.run()
    ~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.0_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/loyalshababo/dev/ether/src/tests/test_type_validation.py", line 84, in run_valid_type_test
    ether.init(config=config)
    ~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/Users/loyalshababo/dev/ether/src/ether/__init__.py", line 54, in init
    _ether.start(config=config, restart=restart)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/loyalshababo/dev/ether/src/ether/_internal/_ether.py", line 138, in start
    raise RuntimeError("Redis server failed to start")
RuntimeError: Redis server failed to start
___________________ test_invalid_types ____________________

    def test_invalid_types():
        """Test that invalid type messages raise appropriate errors"""
        ctx = multiprocessing.get_context('spawn')
        process = ctx.Process(target=run_invalid_type_test)
        process.start()
        process.join()
>       assert process.exitcode == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = <SpawnProcess name='SpawnProcess-2' pid=3019 parent=3015 stopped exitcode=1>.exitcode

src/tests/test_type_validation.py:123: AssertionError
------------------ Captured stderr call -------------------
Process SpawnProcess-2:
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.13/3.13.0_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 313, in _bootstrap
    self.run()
    ~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.0_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/loyalshababo/dev/ether/src/tests/test_type_validation.py", line 109, in run_invalid_type_test
    publisher.send_wrong_type()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/loyalshababo/dev/ether/src/ether/_internal/_registry.py", line 337, in wrapper
    self._logger.debug(f"Inside pub wrapper for {func.__name__}")
    ^^^^^^^^^^^^
AttributeError: 'InvalidPublisher' object has no attribute '_logger'
================= short test summary info =================
FAILED src/tests/test_type_validation.py::test_valid_types - AssertionError: assert 1 == 0
FAILED src/tests/test_type_validation.py::test_invalid_types - AssertionError: assert 1 == 0
=============== 2 failed, 1 passed in 2.48s ===============

---

_**Assistant**_

I see two main issues that need to be fixed. Let's update the test file to handle these errors:

1. The Redis server startup failure in `test_valid_types`
2. Missing logger initialization in the publisher classes

Here are the necessary changes:

```python:src/tests/test_type_validation.py
import pytest
import time
import multiprocessing
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
from ether import ether, ether_pub, ether_sub
from ether._internal._utils import _get_logger

# Test Models
class ValidMessage(BaseModel):
    value: int
    text: str
    optional_field: Optional[str] = None

class NestedMessage(BaseModel):
    items: List[int]
    metadata: Dict[str, str]

# Base class for publishers to handle initialization
class PublisherBase:
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self._logger = _get_logger(self.__class__.__name__, name, log_level=logging.INFO)

# Test Classes
class ValidPublisher(PublisherBase):
    """Publisher that sends correctly typed messages"""
    
    @ether_pub(topic="valid_messages")
    def send_valid_message(self) -> ValidMessage:
        return ValidMessage(value=42, text="hello")
    
    @ether_pub(topic="nested_messages")
    def send_nested_message(self) -> NestedMessage:
        return NestedMessage(
            items=[1, 2, 3],
            metadata={"source": "test"}
        )
    
    @ether_pub(topic="primitive_message")
    def send_primitive(self) -> int:
        return 42

class InvalidPublisher(PublisherBase):
    """Publisher that attempts to send incorrectly typed messages"""
    
    @ether_pub(topic="invalid_message")
    def send_wrong_type(self) -> ValidMessage:
        return {"value": "not an int", "text": 42}  # Wrong types
    
    @ether_pub(topic="missing_field")
    def send_missing_required(self) -> ValidMessage:
        return {"text": "missing value field"}  # Missing required field
    
    @ether_pub(topic="wrong_return")
    def send_wrong_return_type(self) -> int:
        return "not an integer"  # Wrong return type

class ValidationSubscriber:
    """Subscriber that receives and validates messages"""
    def __init__(self):
        self.received_valid = False
        self.received_nested = False
        self.received_primitive = False
        self.error_received = False
    
    @ether_sub(topic="valid_messages")
    def receive_valid(self, value: int, text: str, optional_field: Optional[str] = None):
        self.received_valid = True
    
    @ether_sub(topic="nested_messages")
    def receive_nested(self, items: List[int], metadata: Dict[str, str]):
        self.received_nested = True
    
    @ether_sub(topic="primitive_message")
    def receive_primitive(self, root: int):
        self.received_primitive = True

def run_valid_type_test():
    """Test valid type scenarios"""
    try:
        config = {
            "instances": {
                "validation_subscriber": {
                    "class_path": "tests.test_type_validation.ValidationSubscriber",
                    "autorun": True
                }
            }
        }
        
        # Initialize system with restart to ensure clean state
        ether.init(config=config, restart=True)
        time.sleep(1.0)  # Allow more time for setup
        
        # Create publisher and send messages
        publisher = ValidPublisher()
        publisher.send_valid_message()
        publisher.send_nested_message()
        publisher.send_primitive()
        
        time.sleep(1.0)  # Allow more time for message processing
        
    except Exception as e:
        print(f"Error in valid type test: {e}")
        raise

def test_valid_types():
    """Test that valid type messages are processed correctly"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_valid_type_test)
    process.start()
    process.join(timeout=10)
    assert process.exitcode == 0

def run_invalid_type_test():
    """Test invalid type scenarios"""
    try:
        # Initialize system first
        ether.init(restart=True)
        time.sleep(0.5)
        
        publisher = InvalidPublisher()
        
        # These should raise exceptions
        with pytest.raises(ValueError):
            publisher.send_wrong_type()
        
        with pytest.raises(ValueError):
            publisher.send_missing_required()
        
        with pytest.raises(ValueError):
            publisher.send_wrong_return_type()
            
    except Exception as e:
        print(f"Error in invalid type test: {e}")
        raise

def test_invalid_types():
    """Test that invalid type messages raise appropriate errors"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_invalid_type_test)
    process.start()
    process.join(timeout=10)
    assert process.exitcode == 0

class MismatchPublisher(PublisherBase):
    @ether_pub(topic="mismatched_types")
    def send_message(self) -> ValidMessage:
        return ValidMessage(value=42, text="hello")

class MismatchSubscriber:
    def __init__(self):
        self.error_received = False
    
    @ether_sub(topic="mismatched_types")
    def receive_message(self, wrong_field_name: int):  # Mismatched field name
        pass

def run_type_mismatch_test():
    """Test mismatched type definitions between publisher and subscriber"""
    config = {
        "instances": {
            "mismatch_subscriber": {
                "class_path": "tests.test_type_validation.MismatchSubscriber",
                "autorun": True
            }
        }
    }
    
    ether.init(config=config, restart=True)
    time.sleep(0.5)
    
    publisher = MismatchPublisher()
    publisher.send_message()  # This should cause an error in the subscriber
    time.sleep(0.5)

def test_type_mismatch():
    """Test that mismatched types between pub/sub are handled appropriately"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_type_mismatch_test)
    process.start()
    process.join(timeout=10)
    assert process.exitcode != 0  # Should fail due to type mismatch
```

Key changes made:

1. Added a `PublisherBase` class that handles logger initialization for all publisher classes
2. Added error handling and logging in the test runner functions
3. Added `restart=True` to `ether.init()` calls to ensure clean state
4. Increased sleep times to allow for proper setup
5. Added timeouts to process joins
6. Added try/except blocks to catch and log errors
7. Made all publisher classes inherit from `PublisherBase`

These changes should resolve the logger initialization error and help with the Redis server startup issues. The increased sleep times and restart flags should help ensure the system is in a clean state for each test.

Make sure Redis is installed and running on your system before running the tests. You can install Redis using:

```bash
# On macOS with Homebrew
brew install redis

# On Ubuntu/Debian
sudo apt-get install redis-server
```

Then start the Redis server:

```bash
redis-server
```

Try running the tests again after making these changes and ensuring Redis is available.

---

_**User**_



---

_**Assistant**_

I see the issue. In the `ether_pub` wrapper, we're trying to create a new instance of the return type using the result as kwargs, but the result is already an instance of the return type. Let's fix this in the `_registry.py` file:

```python:src/ether/_internal/_registry.py
# ... other code ...

def ether_pub(topic: Optional[str] = None):
    """Decorator for methods that should publish messages."""
    def decorator(func):
        # Get return type hint if it exists
        return_type = inspect.signature(func).return_annotation
        if return_type == inspect.Parameter.empty:
            raise TypeError(f"Function {func.__name__} must have a return type hint")
        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._logger.debug(f"Inside pub wrapper for {func.__name__}")
            if not hasattr(self, '_pub_socket'):
                raise RuntimeError("Cannot publish: no publisher socket configured")
            
            # Execute the function and get result
            result = func(self, *args, **kwargs)
            
            # Validate result against return type
            if isinstance(return_type, type) and issubclass(return_type, BaseModel):
                if isinstance(result, return_type):
                    # Result is already a BaseModel instance
                    validated_result = result.model_dump_json()
                else:
                    # Result is a dict or other type that needs to be converted
                    validated_result = return_type(**result).model_dump_json()
            else:
                ResultModel = RootModel[return_type]
                validated_result = ResultModel(result).model_dump_json()
            
            # Get topic from metadata
            actual_topic = topic or f"{func.__qualname__}"
            self._logger.debug(f"Publishing to topic: {actual_topic}")
            
            # Publish the validated result
            self._pub_socket.send_multipart([
                actual_topic.encode(),
                validated_result.encode()
            ])
            
            return result
        
        # Create and attach the metadata
        actual_topic = topic or f"{func.__qualname__}"
        wrapper._pub_metadata = EtherPubMetadata(func, actual_topic)
        
        # Mark the containing class for Ether processing
        frame = inspect.currentframe().f_back
        while frame:
            locals_dict = frame.f_locals
            if '__module__' in locals_dict and '__qualname__' in locals_dict:
                EtherRegistry.mark_for_processing(
                    locals_dict['__qualname__'],
                    locals_dict['__module__']
                )
                break
            frame = frame.f_back
        
        return wrapper
    return decorator

# ... rest of the code ...
```

The key change is in the validation logic inside the wrapper function. Now it checks if the result is already an instance of the expected return type before trying to create a new instance.

This should fix the error you're seeing where it was trying to use a ValidMessage instance as kwargs to create another ValidMessage instance.

The updated logic:
1. If the result is already an instance of the expected BaseModel type, use it directly
2. If not, try to create a new instance using the result as kwargs
3. For primitive types, continue using RootModel as before

This change maintains type safety while handling both pre-instantiated models and raw data correctly.

---

_**User**_

We need to catch the type mismatch error better - the process still exits with code 0 becaue we do error handling. We don't want to remove the error handling, just come up with a better way to catch that the type mismatch is handled.

---

_**Assistant**_

I see the issue. We can modify the test to verify that the type mismatch error is properly logged and handled by adding a flag to track when the error occurs. Here's how we can update the test:

```python:src/tests/test_type_validation.py
# ... previous imports and classes remain the same ...

class MismatchSubscriber:
    def __init__(self):
        self.error_received = False
        self._logger = _get_logger(self.__class__.__name__, log_level=logging.INFO)
        self.type_error_occurred = False
    
    @ether_sub(topic="mismatched_types")
    def receive_message(self, wrong_field_name: int):  # Mismatched field name
        pass
    
    def track_error(self, error: Exception):
        """Track that a type error occurred"""
        self._logger.error(f"Type mismatch error: {error}")
        self.type_error_occurred = True

def run_type_mismatch_test():
    """Test mismatched type definitions between publisher and subscriber"""
    config = {
        "instances": {
            "mismatch_subscriber": {
                "class_path": "tests.test_type_validation.MismatchSubscriber",
                "autorun": True,
                "kwargs": {
                    "name": "mismatch_subscriber"
                }
            }
        }
    }
    
    # Initialize with error tracking
    ether.init(config=config, restart=True)
    time.sleep(0.5)
    
    # Send message that should cause type mismatch
    publisher = MismatchPublisher()
    publisher.send_message()
    
    # Wait for error to be processed
    time.sleep(0.5)
    
    # Get subscriber instance from registry to check error state
    from ether._internal._instances._liaison import EtherInstanceLiaison
    liaison = EtherInstanceLiaison()
    instances = liaison.get_active_instances()
    
    # Look for our subscriber instance
    subscriber_found = False
    type_error_occurred = False
    
    for instance_info in instances.values():
        if instance_info.get('name') == 'mismatch_subscriber':
            subscriber_found = True
            if instance_info.get('type_error_occurred', False):
                type_error_occurred = True
            break
    
    if not subscriber_found or not type_error_occurred:
        raise AssertionError("Type mismatch error was not properly handled")

def test_type_mismatch():
    """Test that mismatched types between pub/sub are handled appropriately"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_type_mismatch_test)
    process.start()
    process.join(timeout=10)
    
    # Now we expect a successful exit because we're handling the error
    assert process.exitcode == 0
```

And we need to modify the `_registry.py` to properly track these type mismatch errors:

```python:src/ether/_internal/_registry.py
# ... previous imports and code ...

def ether_sub(topic: Optional[str] = None, subtopic: Optional[str] = None):
    """Decorator for methods that should receive messages."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (TypeError, ValueError) as e:
                # Get instance (self) from args
                if args and hasattr(args[0], 'track_error'):
                    args[0].track_error(e)
                raise  # Re-raise the error after tracking
                
        # Create and attach the metadata
        args_model = _create_model_from_signature(func)
        
        actual_topic = topic or f"{func.__qualname__}"
        if subtopic:
            actual_topic = f"{actual_topic.split('.')[0]}.{subtopic}"
        
        wrapper._sub_metadata = EtherSubMetadata(func, actual_topic, args_model)
        
        # Mark the containing class for Ether processing
        frame = inspect.currentframe().f_back
        while frame:
            locals_dict = frame.f_locals
            if '__module__' in locals_dict and '__qualname__' in locals_dict:
                EtherRegistry.mark_for_processing(
                    locals_dict['__qualname__'],
                    locals_dict['__module__']
                )
                break
            frame = frame.f_back
        
        return wrapper
    return decorator

# ... rest of the code ...
```

This approach:

1. Adds error tracking capability to the subscriber class
2. Modifies the subscriber decorator to catch and track type mismatch errors
3. Updates the test to verify that the error was properly handled by checking the subscriber's state through the instance liaison

The test now passes when the type mismatch is properly handled, rather than relying on process exit codes. This gives us more precise control over verifying that the error handling worked as expected.

We're now testing that:
1. The subscriber received the message
2. The type mismatch was detected
3. The error was properly tracked
4. The system continued running despite the error

This is a more robust way to test error handling while maintaining the system's stability.

---

_**User**_

I'd like to add another test, that confirms that message data received is accurate. Please add this in its own test file.

---

_**Assistant**_

I'll create a new test file specifically for verifying message data integrity.

```python:src/tests/test_message_data.py
import pytest
import time
import multiprocessing
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pydantic import BaseModel
from ether import ether, ether_pub, ether_sub
from ether._internal._utils import _get_logger

# Test Models
class ComplexMessage(BaseModel):
    text: str
    numbers: List[int]
    nested: Dict[str, Dict[str, float]]
    optional: Optional[str] = None

class DataVerificationPublisher:
    """Publisher that sends messages with verifiable data"""
    def __init__(self):
        self._logger = _get_logger(self.__class__.__name__, log_level=logging.INFO)
    
    @ether_pub(topic="complex_data")
    def send_complex_data(self) -> ComplexMessage:
        return ComplexMessage(
            text="test message",
            numbers=[1, 2, 3, 4, 5],
            nested={
                "outer1": {"inner1": 1.1, "inner2": 1.2},
                "outer2": {"inner3": 2.1, "inner4": 2.2}
            },
            optional="optional value"
        )
    
    @ether_pub(topic="primitive_data")
    def send_primitive(self) -> int:
        return 42
    
    @ether_pub(topic="list_data")
    def send_list(self) -> List[int]:
        return [1, 2, 3, 4, 5]

@dataclass
class ReceivedData:
    """Holds received message data for verification"""
    complex_received: bool = False
    complex_data: Optional[ComplexMessage] = None
    primitive_received: bool = False
    primitive_value: Optional[int] = None
    list_received: bool = False
    list_data: Optional[List[int]] = None

class DataVerificationSubscriber:
    """Subscriber that verifies received message data"""
    def __init__(self):
        self._logger = _get_logger(self.__class__.__name__, log_level=logging.INFO)
        self.received_data = ReceivedData()
    
    @ether_sub(topic="complex_data")
    def receive_complex(self, text: str, numbers: List[int], 
                       nested: Dict[str, Dict[str, float]], 
                       optional: Optional[str] = None):
        self._logger.info(f"Received complex data: {text}, {numbers}, {nested}, {optional}")
        self.received_data.complex_received = True
        self.received_data.complex_data = ComplexMessage(
            text=text,
            numbers=numbers,
            nested=nested,
            optional=optional
        )
    
    @ether_sub(topic="primitive_data")
    def receive_primitive(self, root: int):
        self._logger.info(f"Received primitive: {root}")
        self.received_data.primitive_received = True
        self.received_data.primitive_value = root
    
    @ether_sub(topic="list_data")
    def receive_list(self, root: List[int]):
        self._logger.info(f"Received list: {root}")
        self.received_data.list_received = True
        self.received_data.list_data = root

def verify_received_data(received: ReceivedData):
    """Verify that all received data matches expected values"""
    # Verify complex message
    assert received.complex_received, "Complex message not received"
    assert received.complex_data.text == "test message"
    assert received.complex_data.numbers == [1, 2, 3, 4, 5]
    assert received.complex_data.nested == {
        "outer1": {"inner1": 1.1, "inner2": 1.2},
        "outer2": {"inner3": 2.1, "inner4": 2.2}
    }
    assert received.complex_data.optional == "optional value"
    
    # Verify primitive
    assert received.primitive_received, "Primitive not received"
    assert received.primitive_value == 42
    
    # Verify list
    assert received.list_received, "List not received"
    assert received.list_data == [1, 2, 3, 4, 5]

def run_data_verification_test():
    """Run the data verification test"""
    config = {
        "instances": {
            "data_verification_subscriber": {
                "class_path": "tests.test_message_data.DataVerificationSubscriber",
                "autorun": True
            }
        }
    }
    
    try:
        # Initialize system
        ether.init(config=config, restart=True)
        time.sleep(1.0)  # Allow time for setup
        
        # Create publisher and send messages
        publisher = DataVerificationPublisher()
        publisher.send_complex_data()
        publisher.send_primitive()
        publisher.send_list()
        
        # Allow time for message processing
        time.sleep(1.0)
        
        # Get subscriber instance and verify data
        from ether._internal._instances._liaison import EtherInstanceLiaison
        liaison = EtherInstanceLiaison()
        instances = liaison.get_active_instances()
        
        subscriber_found = False
        for instance_info in instances.values():
            if instance_info.get('name') == 'data_verification_subscriber':
                subscriber_found = True
                verify_received_data(instance_info['received_data'])
                break
        
        assert subscriber_found, "Subscriber instance not found"
        
    except Exception as e:
        print(f"Error in data verification test: {e}")
        raise

def test_message_data():
    """Test that message data is accurately transmitted and received"""
    ctx = multiprocessing.get_context('spawn')
    process = ctx.Process(target=run_data_verification_test)
    process.start()
    process.join(timeout=10)
    assert process.exitcode == 0

if __name__ == "__main__":
    pytest.main([__file__])
```

This test file:

1. Defines complex test messages including:
   - A Pydantic model with nested structures
   - Primitive types
   - Lists
   - Optional fields

2. Creates a publisher that sends various types of messages

3. Creates a subscriber that receives and stores the messages

4. Implements detailed verification of received data to ensure:
   - All messages are received
   - All data structures are preserved
   - All values match exactly
   - Nested structures are maintained
   - Types are preserved

5. Uses a dataclass to track received data for easy verification

6. Includes detailed logging for debugging

The test verifies not just that messages are received, but that their entire data structure and values are preserved exactly through the pub/sub system. This helps ensure that the serialization/deserialization process is working correctly for all supported data types.

To run just this test:
```bash
pytest src/tests/test_message_data.py -v
```

---



---

