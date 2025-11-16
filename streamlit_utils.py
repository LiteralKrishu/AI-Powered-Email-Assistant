"""
Shared utilities for Streamlit app: retry logic, config, error handling.
"""

import os
import time
import httpx
import streamlit as st
from typing import Optional, Dict, Any, Callable
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def get_api_base_url() -> str:
    """
    Get FastAPI base URL from environment or Streamlit config.
    Priority: env var > sidebar setting > default
    """
    env_url = os.getenv("FASTAPI_BASE_URL")
    if env_url:
        return env_url
    
    # Check if already in session state (from sidebar)
    if "api_base" in st.session_state:
        return st.session_state.api_base
    
    # Default
    return "http://localhost:8000"


def set_api_base_url(url: str):
    """Store API base URL in session state."""
    st.session_state["api_base"] = url


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, retry_count: int = 0):
        self.message = message
        self.status_code = status_code
        self.retry_count = retry_count
        super().__init__(self.message)


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    timeout: float = 20.0
) -> Callable:
    """
    Decorator for HTTP calls with exponential backoff retry logic.
    
    Args:
        max_retries: number of retry attempts (not including initial)
        backoff_factor: multiplier for delay between retries (1s, 2s, 4s...)
        timeout: HTTP request timeout in seconds
    
    Raises:
        APIError: after max retries exceeded or on client errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, timeout=timeout, **kwargs)
                
                except httpx.ConnectError as e:
                    last_exception = APIError(
                        f"Cannot connect to API: {str(e)}",
                        retry_count=attempt
                    )
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt)
                        st.warning(
                            f"⚠️ Connection failed. Retrying in {delay:.1f}s... "
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay)
                    else:
                        st.error(
                            f"❌ API connection failed after {max_retries + 1} attempts. "
                            f"Ensure FastAPI server is running on {get_api_base_url()}"
                        )
                
                except httpx.TimeoutException as e:
                    last_exception = APIError(
                        f"Request timeout: {str(e)}",
                        retry_count=attempt
                    )
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt)
                        st.warning(
                            f"⏱️  Request timed out. Retrying in {delay:.1f}s... "
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay)
                    else:
                        st.error(
                            f"❌ Request timed out after {max_retries + 1} attempts. "
                            f"Try increasing timeout or checking server load."
                        )
                
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    if status >= 500:
                        # Server error — retry
                        last_exception = APIError(
                            f"Server error {status}: {e.response.text[:200]}",
                            status_code=status,
                            retry_count=attempt
                        )
                        if attempt < max_retries:
                            delay = backoff_factor * (2 ** attempt)
                            st.warning(
                                f"⚠️  Server error {status}. Retrying in {delay:.1f}s... "
                                f"(attempt {attempt + 1}/{max_retries + 1})"
                            )
                            time.sleep(delay)
                        else:
                            st.error(
                                f"❌ Server returned error {status} after {max_retries + 1} attempts. "
                                f"Check FastAPI logs for details."
                            )
                    else:
                        # Client error — do not retry
                        raise APIError(
                            f"API error {status}: {e.response.text[:500]}",
                            status_code=status,
                            retry_count=attempt
                        )
                
                except httpx.RequestError as e:
                    last_exception = APIError(
                        f"Request error: {str(e)}",
                        retry_count=attempt
                    )
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt)
                        st.warning(
                            f"⚠️  Request failed. Retrying in {delay:.1f}s... "
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay)
                    else:
                        st.error(
                            f"❌ Request failed after {max_retries + 1} attempts: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


@retry_with_backoff(max_retries=3, backoff_factor=1.0, timeout=20.0)
def api_get(endpoint: str, timeout: float = 20.0, **kwargs) -> Dict[str, Any]:
    """GET request with retry logic."""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
    
    with httpx.Client() as client:
        resp = client.get(url, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp.json()


@retry_with_backoff(max_retries=3, backoff_factor=1.0, timeout=20.0)
def api_post(endpoint: str, data: Optional[Dict] = None, timeout: float = 20.0, **kwargs) -> Dict[str, Any]:
    """POST request with retry logic."""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
    
    with httpx.Client() as client:
        resp = client.post(url, json=data, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp.json()


@retry_with_backoff(max_retries=3, backoff_factor=1.0, timeout=20.0)
def api_put(endpoint: str, data: Optional[Dict] = None, timeout: float = 20.0, **kwargs) -> Dict[str, Any]:
    """PUT request with retry logic."""
    base_url = get_api_base_url()
    url = f"{base_url}{endpoint}"
    
    with httpx.Client() as client:
        resp = client.put(url, json=data, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp.json()


def safe_api_call(
    func: Callable,
    error_message: str = "API request failed",
    return_default: Optional[Any] = None
) -> Optional[Any]:
    """
    Safely call an API function and handle APIError gracefully.
    
    Args:
        func: function to call (should raise APIError on failure)
        error_message: custom error message prefix
        return_default: value to return on error
    
    Returns:
        result of func() or return_default on error
    """
    try:
        return func()
    except APIError as e:
        st.error(f"❌ {error_message}: {e.message}")
        return return_default
    except Exception as e:
        st.error(f"❌ {error_message}: {str(e)}")
        return return_default
