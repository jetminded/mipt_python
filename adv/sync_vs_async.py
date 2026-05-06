from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asyncronously fetch (get-request) single url using provided session
    :param session: aiohttp session object
    :param url: target http url
    :return: fetched text
    """
    async with session.get(url) as s:
        return await s.text()


def sync_fetch(session: requests.Session, url: str) -> str:
    """
    Syncronously fetch (get-request) single url using provided session
    :param session: requests session object
    :param url: target http url
    :return: fetched text
    """
    return session.get(url).text

def sync_requests(urls: list[str]) -> list[str]:
    """
    Fetch provided urls with requests WITHOUT concurrency
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    session = requests.Session()
    return [sync_fetch(session, url) for url in urls]


async def async_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls using aiohttp
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    async with aiohttp.ClientSession() as session:
        return [await async_fetch(session, url) for url in urls]

def threaded_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls with requests in different threads
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    session = requests.Session()
    surls = [(session, url) for url in urls]

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        results = executor.map(sync_fetch, surls)
        return list(results)
