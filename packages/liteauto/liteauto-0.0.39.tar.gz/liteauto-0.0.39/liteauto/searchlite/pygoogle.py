from concurrent.futures.thread import ThreadPoolExecutor

from googlesearch import search


def _handle_single_query(query,max_urls=5,unique=True):
    urls = list(search(query, num_results=max_urls, unique=unique))
    https_urls = [url for url in urls if 'http' == url[:4]]
    return https_urls
def google(query: str|list, max_urls=5, unique=True):
    if isinstance(query,str):
        return _handle_single_query(query=query,max_urls=max_urls,unique=unique)
    with ThreadPoolExecutor(max_workers=4) as executors:
        return list(executors.map(_handle_single_query,query))
