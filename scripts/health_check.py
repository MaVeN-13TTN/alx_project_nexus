#!/usr/bin/env python3
"""
Health check script for post-deployment testing.
"""
import sys
from urllib.parse import urlparse
from requests import get
from requests.exceptions import RequestException, Timeout, ConnectionError


def health_check(url: str, timeout: int = 30) -> bool:
    # Validate URL to prevent SSRF
    parsed = urlparse(url)
    if not parsed.scheme in ['http', 'https'] or not parsed.netloc:
        print(f"❌ Invalid URL format: {url}")
        return False
    """
    Perform health check on the given URL.
    
    Args:
        url: The health check endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if health check passes, False otherwise
    """
    try:
        print(f"🔍 Checking health endpoint: {url}")
        response = get(url, timeout=timeout)
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
            
    except Timeout:
        print(f"❌ Health check failed: Request timeout after {timeout}s")
        return False
    except ConnectionError:
        print("❌ Health check failed: Connection error")
        return False
    except RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during health check: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python health_check.py <health_check_url>")
        sys.exit(1)
    
    health_url = sys.argv[1]
    success = health_check(health_url)
    
    if not success:
        print("❌ Health check failed", file=sys.stderr)
        sys.exit(1)