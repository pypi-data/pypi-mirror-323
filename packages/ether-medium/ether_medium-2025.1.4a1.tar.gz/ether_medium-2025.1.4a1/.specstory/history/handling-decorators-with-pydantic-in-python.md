## SpecStory

## Handling Decorators with Pydantic in Python (1/16/2025, 12:07:54 PM)

_**User**_

Can we handle the case where there is no return from a method and also the case where there is inputs when we decorate with ether_pub and ether_sub and do all the pydantic stuff?

---

_**Assistant**_

I'll help modify the code to handle these cases. We need to update both the `_ether_pub` and `_ether_sub` decorators to handle optional returns and inputs more gracefully.

Here are the changes needed:

```python:src/ether/_internal/_registry.py
# ... (earlier code remains the same)

def _create_model_from_signature(func) -> Type[BaseModel]:
    """Creates a Pydantic model from a function's signature"""
    sig = inspect.signature(func)
    fields = {}
    
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
        default = param.default if param.default != inspect.Parameter.empty else ...
        
        # Handle root model case
        if name == 'root':
            return RootModel[annotation]
        
        fields[name] = (annotation, default)
    
    # If no fields (other than self), return a model with an empty dict
    if not fields:
        fields = {"_empty": (dict, {})}
    
    model_name = f"{func.__name__}Args"
    return create_model(model_name, **fields)

def _ether_pub(topic: Optional[str] = None):
    """Decorator for methods that should publish messages."""
    def decorator(func):
        # Get return type hint if it exists
        sig = inspect.signature(func)
        return_type = sig.return_annotation
        
        # If no return type specified, use dict as default
        if return_type == inspect.Parameter.empty:
            return_type = dict
        # Handle None return type (specified as None or type(None))
        elif return_type in (None, type(None)):
            return_type = dict
        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the function and get result
            result = func(self, *args, **kwargs)
            try:
                self._logger.debug(f"Inside pub wrapper for {func.__name__}")
                if not hasattr(self, '_pub_socket'):
                    raise RuntimeError("Cannot publish: no publisher socket configured")
                
                # Handle None result
                if result is None:
                    result = {}
                
                # Validate and serialize result
                if isinstance(return_type, type) and issubclass(return_type, BaseModel):
                    validated_result = return_type(**result).model_dump_json()
                else:
                    ResultModel = RootModel[return_type]
                    validated_result = ResultModel(result).model_dump_json()
                
                actual_topic = topic or f"{func.__qualname__}"
                self._logger.debug(f"Publishing to topic: {actual_topic}")
                
                self._pub_socket.send_multipart([
                    actual_topic.encode(),
                    validated_result.encode()
                ])
            except Exception as e:
                self._logger.error(f"Error in pub wrapper: {e}")
                # we never want to crash basic operation of the underlying user code
                pass
            
            return result
        
        # Create and attach the metadata
        actual_topic = topic or f"{func.__qualname__}"
        wrapper._pub_metadata = EtherPubMetadata(func, actual_topic)
        
        # Mark the containing class for Ether processing
        frame = inspect.currentframe().f_back
        while frame:
            locals_dict = frame.f_locals
            if '__module__' in locals_dict and '__qualname__' in locals_dict:
                EtherRegistry().mark_for_processing(
                    locals_dict['__qualname__'],
                    locals_dict['__module__']
                )
                break
            frame = frame.f_back
        
        return wrapper
    return decorator
```

These changes:

1. For `_ether_pub`:
   - Handle cases where no return type is specified by defaulting to `dict`
   - Handle explicit `None` return types by treating them as empty dictionaries
   - Handle `None` return values by converting them to empty dictionaries

2. For `_create_model_from_signature` (used by `_ether_sub`):
   - Handle cases where there are no input parameters by creating a model with an empty dict field
   - Continue to use `Any` as the default type for parameters without type hints

The changes ensure that:
- Methods decorated with `@ether_pub` can return `None` or have no return type annotation
- Methods decorated with `@ether_sub` can have no parameters
- Type validation still occurs when types are specified
- Empty/None values are handled gracefully

This makes the decorators more flexible while maintaining type safety when types are specified. The system will now work with methods like:

```python
@ether_pub()
def my_method_no_return(self):
    # No return statement

@ether_pub()
def my_method_none_return(self) -> None:
    return None

@ether_sub("some.topic")
def my_method_no_params(self):
    # No parameters
```

---

_**User**_

Great, one thing, we get this warning:
Can we change our approach to avoid this?

---

_**Assistant**_

Yes, we can avoid the underscore warning by using a different approach for handling empty models. Here's the fix:

```python:src/ether/_internal/_registry.py
def _create_model_from_signature(func) -> Type[BaseModel]:
    """Creates a Pydantic model from a function's signature"""
    sig = inspect.signature(func)
    fields = {}
    
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
        default = param.default if param.default != inspect.Parameter.empty else ...
        
        # Handle root model case
        if name == 'root':
            return RootModel[annotation]
        
        fields[name] = (annotation, default)
    
    # If no fields (other than self), create a model with a non-underscore field
    if not fields:
        fields = {"data": (dict, {})}
    
    model_name = f"{func.__name__}Args"
    return create_model(model_name, **fields)
```

This change:
1. Replaces `_empty` with `data` as the field name for empty models
2. Still maintains the same functionality but avoids the Pydantic warning about underscore-prefixed fields
3. Uses a more semantic field name that better represents its purpose

Now when there are no parameters, the model will have a `data` field instead of `_empty`, which is both more semantically meaningful and avoids the warning.

---

_**User**_

We're seeing this error:
2025-01-16 12:15:25.966 - DataCollector:collector1:54131 - ERROR - Error in run loop: DataCollector.summarize() got an unexpected keyword argument 'data'

Instead of directly matching the schema for the incoming message model and the sub method signature, can we just intersect them?

---

_**Assistant**_

Yes, we can modify the code to only pass the matching arguments between the incoming message and the method signature. Here's how we can update the `receive_single_message` method:

```python:src/ether/_internal/_registry.py
def receive_single_message(self, timeout=1000):
    if self._sub_socket and self._sub_socket.poll(timeout=timeout):
        message = self._sub_socket.recv_multipart()
        topic = message[0].decode()
        data = json.loads(message[1].decode())
        
        self._logger.debug(f"Received message: topic={topic}, data={data}")
        
        if topic in self._sub_topics:
            metadata = self._sub_metadata.get(topic)
            if metadata:
                # Get the method's signature parameters
                sig = inspect.signature(metadata.func)
                valid_params = sig.parameters.keys()
                
                # Remove 'self' from valid params if present
                if 'self' in valid_params:
                    valid_params = [p for p in valid_params if p != 'self']
                
                # If using root model, pass the entire data as 'root'
                if isinstance(metadata.args_model, type) and issubclass(metadata.args_model, RootModel):
                    args = {'root': metadata.args_model(data).root}
                else:
                    # Validate data with the model
                    model_instance = metadata.args_model(**data)
                    validated_data = model_instance.model_dump()
                    
                    # Only pass the arguments that exist in the method signature
                    args = {k: v for k, v in validated_data.items() if k in valid_params}
                
                metadata.func(self, **args)
```

This change:
1. Gets the method's signature parameters
2. Filters out 'self' if present
3. For RootModel, keeps the existing behavior
4. For regular models:
   - Validates the incoming data using the Pydantic model
   - Only passes the arguments that exist in both the validated data and the method signature

This way, if the incoming message has extra fields or if our default 'data' field is present but not needed, they won't be passed to the method. This should resolve the "unexpected keyword argument" error while maintaining type validation.

---

_**User**_

Hell yeah, that worked!

---

_**Assistant**_

Great! The solution we implemented is much more robust because:

1. It respects the method's signature by only passing arguments that the method actually expects
2. Still maintains type validation through Pydantic
3. Handles both cases:
   - When methods have no parameters (by filtering out extra fields)
   - When incoming messages have extra data (by only passing matching fields)

This makes the pub/sub system more flexible and less prone to errors, following the principle of being "liberal in what you accept, conservative in what you send". The subscriber methods now only receive exactly what they ask for, even if more data is available in the message.

Would you like to make any other improvements to the system?

---



---

