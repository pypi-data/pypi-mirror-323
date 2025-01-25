## SpecStory

## Using Stop Signal for Graceful Shutdown in PubSub (11/15/2024, 4:29:41 PM)

_**User**_

Shouldn't we be using a stop signal here as setup in run_pubsub

---

_**Assistant**_

Yes, you're absolutely right! Since we set up signal handlers in `_run_pubsub()` to handle graceful shutdown, we should use those instead of directly calling terminate. Here's how we should modify that section:

```python:src/ether/_internal/_ether.py
            try:
                if self._pubsub_process:
                    self._logger.debug("Shutting down PubSub proxy")
                    # Send SIGTERM to trigger graceful shutdown
                    os.kill(self._pubsub_process.pid, signal.SIGTERM)
                    self._pubsub_process.join(timeout=2)
                    if self._pubsub_process.is_alive():
                        self._logger.warning("PubSub proxy didn't stop gracefully, killing")
                        self._pubsub_process.kill()
                        self._pubsub_process.join(timeout=1)
                    self._pubsub_process = None
```

This change:
1. Uses `os.kill()` to send a SIGTERM signal to the process instead of calling `terminate()`
2. Still keeps the fallback to `kill()` if the graceful shutdown doesn't complete within 2 seconds
3. Takes advantage of the signal handlers we set up in `_run_pubsub()` to ensure proper cleanup of the ZMQ proxy

This will allow the proxy to clean up its resources properly before shutting down, which is especially important for ZMQ sockets.

---



---

