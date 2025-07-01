# async_helpers

> Async helper utilities for mdvis.

Common async patterns and utilities used throughout the codebase.

## Overview

- **Classes:** 1
- **Functions:** 9
- **Lines of Code:** 317

## Imports
- **import** `asyncio`
- **import** `time`
- **from** `contextlib` **import** `asynccontextmanager`
- **from** `typing` **import** `Any, Callable, List, Optional, TypeVar, Union, Awaitable`
- **from** `pathlib` **import** `Path`
- **import** `logging`

## Classes
### AsyncProgress {#class-asyncprogress}

> Simple async progress tracker for long-running operations.


#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self, total: int, name: str = 'Progress')`
##### update {#method-update}

> Update progress by increment..

**Signature:** `def update(self, increment: int = 1) -> None`
##### is_complete {#method-is-complete}

> Check if progress is complete..

**Signature:** `def is_complete(self) -> bool`

## Functions
### gather_with_limit {#function-gather-with-limit}

> Run coroutines concurrently with a maximum concurrency limit.

Args:
    *coroutines: Coroutines to run
    limit: Maximum number of concurrent coroutines
    return_exceptions: Whether to return exceptions instead of raising
    
Returns:
    List of results in the same order as input coroutines

**Signature:** `async def gather_with_limit(*coroutines: Awaitable[T], limit: int = 10, return_exceptions: bool = False) -> List[Union[T, Exception]]`
### batch_process {#function-batch-process}

> Process items in batches to avoid overwhelming resources.

Args:
    items: Items to process
    async_func: Async function to apply to each item
    batch_size: Number of items to process concurrently
    delay_between_batches: Delay between batches in seconds
    
Returns:
    List of results

**Signature:** `async def batch_process(items: List[T], async_func: Callable[[T], Awaitable[Any]], batch_size: int = 10, delay_between_batches: float = 0.0) -> List[Any]`
### async_timer {#function-async-timer}

> Async context manager for timing operations.

Args:
    name: Name of the operation being timed

**Signature:** `async def async_timer(name: str = 'operation')`
### retry_with_backoff {#function-retry-with-backoff}

> Retry an async function with exponential backoff.

Args:
    async_func: Async function to retry
    max_retries: Maximum number of retry attempts
    base_delay: Initial delay between retries
    max_delay: Maximum delay between retries
    backoff_factor: Multiplier for delay on each retry
    exceptions: Tuple of exceptions to catch and retry on
    
Returns:
    Result of the function call
    
Raises:
    The last exception if all retries are exhausted

**Signature:** `async def retry_with_backoff(async_func: Callable[[], Awaitable[T]], max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)) -> T`
### run_with_timeout {#function-run-with-timeout}

> Run a coroutine with a timeout.

Args:
    coro: Coroutine to run
    timeout: Timeout in seconds
    timeout_message: Custom timeout error message
    
Returns:
    Result of the coroutine
    
Raises:
    asyncio.TimeoutError: If timeout is exceeded

**Signature:** `async def run_with_timeout(coro: Awaitable[T], timeout: float, timeout_message: Optional[str] = None) -> T`
### safe_gather {#function-safe-gather}

> Safely gather coroutines with proper exception handling and logging.

Args:
    *coroutines: Coroutines to gather
    return_exceptions: Whether to return exceptions instead of raising
    
Returns:
    List of results or exceptions

**Signature:** `async def safe_gather(*coroutines: Awaitable[T], return_exceptions: bool = True) -> List[Union[T, Exception]]`
### async_map {#function-async-map}

> Apply an async function to a list of items with concurrency control.

Args:
    async_func: Async function to apply
    items: Items to process
    max_concurrency: Maximum concurrent operations
    
Returns:
    List of results in the same order as input items

**Signature:** `async def async_map(async_func: Callable[[T], Awaitable[Any]], items: List[T], max_concurrency: int = 10) -> List[Any]`
### ensure_async {#function-ensure-async}

> Ensure a function or coroutine is awaited properly.

Args:
    func_or_coro: Either a function that returns a value or a coroutine
    
Returns:
    The result of the function or coroutine

**Signature:** `async def ensure_async(func_or_coro: Union[Callable[[], T], Awaitable[T]]) -> T`
### async_filter {#function-async-filter}

> Filter items using an async predicate function.

Args:
    async_predicate: Async function that returns True for items to keep
    items: Items to filter
    max_concurrency: Maximum concurrent predicate checks
    
Returns:
    Filtered list of items

**Signature:** `async def async_filter(async_predicate: Callable[[T], Awaitable[bool]], items: List[T], max_concurrency: int = 10) -> List[T]`
