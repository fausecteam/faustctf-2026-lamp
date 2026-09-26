import random

def rand():
    random.choice([
        f"python-requests/2.{random.randint(0, 47)}.{random.randint(0, 5)}",
        f"python-urllib/3.{random.randint(0, 27)}",
        f"python-httpx/0.{random.randint(0, 34)}.{random.randint(0, 5)}",
        f"aiohttp/3.{random.randint(0, 20)}.{random.randint(0, 5)}",

        f"curl/7.{random.randint(0, 89)}.{random.randint(0, 1)}",
        f"curl/8.{random.randint(0, 30)}.{random.randint(0, 1)}",

        f"axios/0.{random.randint(1, 33)}.{random.randint(0, 3)}",
        f"axios/1.{random.randint(0, 20)}.{random.randint(0, 3)}",

        "Go-http-client/2.0",
        "Go-http-client/1.1",

	# some hardcoded browsers
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    ])
