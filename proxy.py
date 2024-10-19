import aiohttp
import asyncio
from aiohttp_socks import ProxyConnector
import time

# الدالة لاختبار البروكسي بشكل غير متزامن مع دعم HTTP و SOCKS4/5
async def check_proxy_async(proxy, timeout=5, proxy_type='http'):
    try:
        if proxy_type == 'http':
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}',
            }
            connector = aiohttp.TCPConnector()  # اتصال HTTP عادي
        else:
            connector = ProxyConnector.from_url(f'{proxy_type}://{proxy}')  # اتصال SOCKS

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get('https://httpbin.org/ip', timeout=timeout) as response:
                if response.status == 200:
                    return proxy, True
                else:
                    return proxy, False
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return proxy, False

# الدالة لفحص البروكسيات المتعددة بشكل غير متزامن
async def filter_valid_proxies_async(proxy_list, proxy_type='http', timeout=5):
    tasks = [check_proxy_async(proxy, timeout, proxy_type) for proxy in proxy_list]
    valid_proxies = []
    for task in asyncio.as_completed(tasks):
        proxy, is_valid = await task
        if is_valid:
            print(f"Proxy {proxy} ({proxy_type}) is valid.")
            valid_proxies.append(proxy)
        else:
            print(f"Proxy {proxy} ({proxy_type}) is invalid.")
    return valid_proxies

# الدالة لقراءة البروكسيات من ملف
def load_proxies_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = file.readlines()
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        return proxies
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []

# الدالة لحفظ البروكسيات الصالحة في ملف جديد
def save_valid_proxies(valid_proxies, output_file="valid_proxies.txt"):
    try:
        with open(output_file, 'w') as file:
            for proxy in valid_proxies:
                file.write(f"{proxy}\n")
        print(f"Valid proxies saved to {output_file}.")
    except Exception as e:
        print(f"Error saving valid proxies: {e}")

# الدالة الرئيسية لاختبار البروكسيات المتعددة
async def main(proxy_file, proxy_type='http', timeout=5):
    proxies = load_proxies_from_file(proxy_file)
    if proxies:
        print(f"Loaded {len(proxies)} proxies from {proxy_file}.")
        
        start_time = time.time()
        valid_proxies = await filter_valid_proxies_async(proxies, proxy_type=proxy_type, timeout=timeout)
        end_time = time.time()
        
        print(f"Found {len(valid_proxies)} valid proxies out of {len(proxies)}.")
        print(f"Time taken: {end_time - start_time:.2f} seconds.")
        
        if valid_proxies:
            save_valid_proxies(valid_proxies, "valid_proxies_async.txt")
    else:
        print("No proxies to check.")

# تنفيذ الكود مع دعم البروكسيات HTTP و SOCKS4 و SOCKS5
if __name__ == "__main__":
    proxy_file = "proxies.txt"  # يمكن تحديد الملف من خلال الواجهة
    proxy_type = 'http'  # يمكن تغييرها إلى 'socks5' أو 'socks4' لاختبار بروكسيات SOCKS

    # تشغيل الفحص بشكل غير متزامن
    asyncio.run(main(proxy_file, proxy_type=proxy_type, timeout=5))
