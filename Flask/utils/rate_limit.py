import asyncio
import aiohttp
from urllib.parse import urlparse


def format_url(url):
    """
    Formats the URL to ensure it starts with 'https://' if not provided.
    """
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    return url.lower()


async def send_request(session, url, request_number):
    """
    Sends a single request asynchronously and returns the result.
    """
    try:
        async with session.get(url) as response:
            content_length = len(await response.read())
            return {
                'request_number': request_number,
                'status_code': response.status,
                'response_time': f"{response.headers.get('X-Request-Duration', 'N/A')}ms",
                'content_length': content_length,
                'error': None,
            }
    except Exception as e:
        return {
            'request_number': request_number,
            'status_code': 'Error',
            'response_time': 'N/A',
            'content_length': 'N/A',
            'error': str(e),
        }


async def perform_rate_limit_test_async(target_url, num_requests):
    """
    Asynchronously tests the target endpoint for rate-limiting behavior.
    """
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_request(session, target_url, i + 1) for i in range(num_requests)
        ]
        results = await asyncio.gather(*tasks)
    return results


def perform_rate_limit_test(target_url, num_requests):
    """
    Wrapper for running the asynchronous rate limit test.
    """
    return asyncio.run(perform_rate_limit_test_async(target_url, num_requests))