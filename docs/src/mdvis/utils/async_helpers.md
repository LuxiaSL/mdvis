---
title: async_helpers
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/utils/async_helpers.py
package: mdvis.utils
stats:
  classes: 1
  functions: 9
  lines_of_code: 317
  complexity: 32
tags:
  - python
  - module
  - oop
  - async
---

# async_helpers

> [!info] Documentation
> Async helper utilities for mdvis.
> 
> Common async patterns and utilities used throughout the codebase.

## Table of Contents

### Classes
- [[#class-asyncprogress|AsyncProgress]]

### Functions
- [[#function-gather-with-limit|gather_with_limit]]
- [[#function-batch-process|batch_process]]
- [[#function-async-timer|async_timer]]
- [[#function-retry-with-backoff|retry_with_backoff]]
- [[#function-run-with-timeout|run_with_timeout]]
- [[#function-safe-gather|safe_gather]]
- [[#function-async-map|async_map]]
- [[#function-ensure-async|ensure_async]]
- [[#function-async-filter|async_filter]]


## Imports

- **import** `asyncio`
- **import** `time`
- **from** `contextlib` **import** `asynccontextmanager`
- **from** `typing` **import** `Any`, `Callable`, `List`, `Optional`, `TypeVar`, `Union`, `Awaitable`
- **from** `pathlib` **import** `Path`
- **import** `logging`

## Classes

### AsyncProgress {#class-asyncprogress}

> [!info] Documentation
> Simple async progress tracker for long-running operations.

#### Methods

##### update {#method-update}

**Signature:** `def update(self, increment: int = 1) -> None`

> [!info] Documentation
> Update progress by increment.

**Returns:** `None`


##### is_complete {#method-is-complete}

**Signature:** `def is_complete(self) -> bool`

> [!info] Documentation
> Check if progress is complete.

**Returns:** `bool`



## Functions

### gather_with_limit {#function-gather-with-limit}

**Signature:** `async def gather_with_limit(*coroutines: Awaitable[T], limit: int = 10, return_exceptions: bool = False) -> List[Union[T, Exception]]`

> [!info] Documentation
> Run coroutines concurrently with a maximum concurrency limit.
> 
> Args:
>     *coroutines: Coroutines to run
>     limit: Maximum number of concurrent coroutines
>     return_exceptions: Whether to return exceptions instead of raising
>     
> Returns:
>     List of results in the same order as input coroutines

**Returns:** `List[Union[T, Exception]]`


### batch_process {#function-batch-process}

**Signature:** `async def batch_process(items: List[T], async_func: Callable[[T], Awaitable[Any]], batch_size: int = 10, delay_between_batches: float = 0.0) -> List[Any]`

> [!info] Documentation
> Process items in batches to avoid overwhelming resources.
> 
> Args:
>     items: Items to process
>     async_func: Async function to apply to each item
>     batch_size: Number of items to process concurrently
>     delay_between_batches: Delay between batches in seconds
>     
> Returns:
>     List of results

**Returns:** `List[Any]`


### async_timer {#function-async-timer}

**Signature:** `async def async_timer(name: str = 'operation')`

> [!info] Documentation
> Async context manager for timing operations.
> 
> Args:
>     name: Name of the operation being timed


### retry_with_backoff {#function-retry-with-backoff}

**Signature:** `async def retry_with_backoff(async_func: Callable[[], Awaitable[T]], max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)) -> T`

> [!info] Documentation
> Retry an async function with exponential backoff.
> 
> Args:
>     async_func: Async function to retry
>     max_retries: Maximum number of retry attempts
>     base_delay: Initial delay between retries
>     max_delay: Maximum delay between retries
>     backoff_factor: Multiplier for delay on each retry
>     exceptions: Tuple of exceptions to catch and retry on
>     
> Returns:
>     Result of the function call
>     
> Raises:
>     The last exception if all retries are exhausted

**Returns:** `T`


### run_with_timeout {#function-run-with-timeout}

**Signature:** `async def run_with_timeout(coro: Awaitable[T], timeout: float, timeout_message: Optional[str] = None) -> T`

> [!info] Documentation
> Run a coroutine with a timeout.
> 
> Args:
>     coro: Coroutine to run
>     timeout: Timeout in seconds
>     timeout_message: Custom timeout error message
>     
> Returns:
>     Result of the coroutine
>     
> Raises:
>     asyncio.TimeoutError: If timeout is exceeded

**Returns:** `T`


### safe_gather {#function-safe-gather}

**Signature:** `async def safe_gather(*coroutines: Awaitable[T], return_exceptions: bool = True) -> List[Union[T, Exception]]`

> [!info] Documentation
> Safely gather coroutines with proper exception handling and logging.
> 
> Args:
>     *coroutines: Coroutines to gather
>     return_exceptions: Whether to return exceptions instead of raising
>     
> Returns:
>     List of results or exceptions

**Returns:** `List[Union[T, Exception]]`


### async_map {#function-async-map}

**Signature:** `async def async_map(async_func: Callable[[T], Awaitable[Any]], items: List[T], max_concurrency: int = 10) -> List[Any]`

> [!info] Documentation
> Apply an async function to a list of items with concurrency control.
> 
> Args:
>     async_func: Async function to apply
>     items: Items to process
>     max_concurrency: Maximum concurrent operations
>     
> Returns:
>     List of results in the same order as input items

**Returns:** `List[Any]`


### ensure_async {#function-ensure-async}

**Signature:** `async def ensure_async(func_or_coro: Union[Callable[[], T], Awaitable[T]]) -> T`

> [!info] Documentation
> Ensure a function or coroutine is awaited properly.
> 
> Args:
>     func_or_coro: Either a function that returns a value or a coroutine
>     
> Returns:
>     The result of the function or coroutine

**Returns:** `T`


### async_filter {#function-async-filter}

**Signature:** `async def async_filter(async_predicate: Callable[[T], Awaitable[bool]], items: List[T], max_concurrency: int = 10) -> List[T]`

> [!info] Documentation
> Filter items using an async predicate function.
> 
> Args:
>     async_predicate: Async function that returns True for items to keep
>     items: Items to filter
>     max_concurrency: Maximum concurrent predicate checks
>     
> Returns:
>     Filtered list of items

**Returns:** `List[T]`


## Source Code

```python
"""
Async helper utilities for mdvis.

Common async patterns and utilities used throughout the codebase.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, Callable, List, Optional, TypeVar, Union, Awaitable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def gather_with_limit(
    *coroutines: Awaitable[T], 
    limit: int = 10,
    return_exceptions: bool = False
) -> List[Union[T, Exception]]:
    """
    Run coroutines concurrently with a maximum concurrency limit.
    
    Args:
        *coroutines: Coroutines to run
        limit: Maximum number of concurrent coroutines
        return_exceptions: Whether to return exceptions instead of raising
        
    Returns:
        List of results in the same order as input coroutines
    """
    semaphore = asyncio.Semaphore(limit)
    
    async def run_with_semaphore(coro):
        async with semaphore:
            return await coro
    
    limited_coros = [run_with_semaphore(coro) for coro in coroutines]
    return await asyncio.gather(*limited_coros, return_exceptions=return_exceptions)


async def batch_process(
    items: List[T],
    async_func: Callable[[T], Awaitable[Any]],
    batch_size: int = 10,
    delay_between_batches: float = 0.0
) -> List[Any]:
    """
    Process items in batches to avoid overwhelming resources.
    
    Args:
        items: Items to process
        async_func: Async function to apply to each item
        batch_size: Number of items to process concurrently
        delay_between_batches: Delay between batches in seconds
        
    Returns:
        List of results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_coroutines = [async_func(item) for item in batch]
        
        try:
            batch_results = await asyncio.gather(*batch_coroutines, return_exceptions=True)
            results.extend(batch_results)
            
            # Log progress
            processed = min(i + batch_size, len(items))
            logger.debug(f"Processed {processed}/{len(items)} items")
            
            # Delay between batches if specified
            if delay_between_batches > 0 and i + batch_size < len(items):
                await asyncio.sleep(delay_between_batches)
                
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
            # Add None results for failed batch
            results.extend([None] * len(batch))
    
    return results


@asynccontextmanager
async def async_timer(name: str = "operation"):
    """
    Async context manager for timing operations.
    
    Args:
        name: Name of the operation being timed
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.debug(f"{name} completed in {elapsed:.2f}s")


async def retry_with_backoff(
    async_func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Retry an async function with exponential backoff.
    
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
    """
    last_exception = None
    delay = base_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await async_func()
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"Function failed after {max_retries} retries: {e}")
                break
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)
    
    raise last_exception


async def run_with_timeout(
    coro: Awaitable[T], 
    timeout: float,
    timeout_message: Optional[str] = None
) -> T:
    """
    Run a coroutine with a timeout.
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        timeout_message: Custom timeout error message
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        message = timeout_message or f"Operation timed out after {timeout}s"
        logger.error(message)
        raise asyncio.TimeoutError(message)


class AsyncProgress:
    """
    Simple async progress tracker for long-running operations.
    """
    
    def __init__(self, total: int, name: str = "Progress"):
        self.total = total
        self.name = name
        self.completed = 0
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> None:
        """Update progress by increment."""
        self.completed = min(self.completed + increment, self.total)
        
        # Log progress at 10% intervals
        percentage = (self.completed / self.total) * 100
        if self.completed == self.total or percentage % 10 == 0:
            elapsed = time.time() - self.start_time
            rate = self.completed / elapsed if elapsed > 0 else 0
            remaining = (self.total - self.completed) / rate if rate > 0 else 0
            
            logger.info(
                f"{self.name}: {self.completed}/{self.total} "
                f"({percentage:.1f}%) - "
                f"Rate: {rate:.1f}/s - "
                f"ETA: {remaining:.0f}s"
            )
    
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.completed >= self.total


async def safe_gather(*coroutines: Awaitable[T], return_exceptions: bool = True) -> List[Union[T, Exception]]:
    """
    Safely gather coroutines with proper exception handling and logging.
    
    Args:
        *coroutines: Coroutines to gather
        return_exceptions: Whether to return exceptions instead of raising
        
    Returns:
        List of results or exceptions
    """
    try:
        results = await asyncio.gather(*coroutines, return_exceptions=return_exceptions)
        
        if return_exceptions:
            # Log any exceptions found
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Coroutine {i} failed: {result}")
        
        return results
    except Exception as e:
        logger.error(f"Unexpected error in safe_gather: {e}")
        return [e] * len(coroutines)


async def async_map(
    async_func: Callable[[T], Awaitable[Any]],
    items: List[T],
    max_concurrency: int = 10
) -> List[Any]:
    """
    Apply an async function to a list of items with concurrency control.
    
    Args:
        async_func: Async function to apply
        items: Items to process
        max_concurrency: Maximum concurrent operations
        
    Returns:
        List of results in the same order as input items
    """
    if not items:
        return []
    
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process_item(item: T) -> Any:
        async with semaphore:
            return await async_func(item)
    
    coroutines = [process_item(item) for item in items]
    return await asyncio.gather(*coroutines, return_exceptions=True)


async def ensure_async(func_or_coro: Union[Callable[[], T], Awaitable[T]]) -> T:
    """
    Ensure a function or coroutine is awaited properly.
    
    Args:
        func_or_coro: Either a function that returns a value or a coroutine
        
    Returns:
        The result of the function or coroutine
    """
    if asyncio.iscoroutine(func_or_coro):
        return await func_or_coro
    elif callable(func_or_coro):
        result = func_or_coro()
        if asyncio.iscoroutine(result):
            return await result
        return result
    else:
        return func_or_coro


async def async_filter(
    async_predicate: Callable[[T], Awaitable[bool]],
    items: List[T],
    max_concurrency: int = 10
) -> List[T]:
    """
    Filter items using an async predicate function.
    
    Args:
        async_predicate: Async function that returns True for items to keep
        items: Items to filter
        max_concurrency: Maximum concurrent predicate checks
        
    Returns:
        Filtered list of items
    """
    if not items:
        return []
    
    # Get predicate results for all items
    results = await async_map(async_predicate, items, max_concurrency)
    
    # Filter items based on predicate results
    filtered_items = []
    for item, keep in zip(items, results):
        if isinstance(keep, bool) and keep:
            filtered_items.append(item)
        elif isinstance(keep, Exception):
            logger.warning(f"Predicate failed for item {item}: {keep}")
    
    return filtered_items
```