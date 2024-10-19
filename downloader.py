import os
import requests
import hashlib
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

# وظيفة للتحقق من سلامة الملف باستخدام SHA256
def verify_file_integrity(file_path, expected_hash):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest() == expected_hash

# وظيفة لإنشاء نسخة احتياطية للملف
def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        os.rename(file_path, backup_path)
        print(f"تم إنشاء نسخة احتياطية للملف: {backup_path}")

# وظيفة لتنزيل الملفات
def download_file(url, folder_path, proxies=None, progress_callback=None):
    local_filename = os.path.join(folder_path, url.split("/")[-1])
    if os.path.exists(local_filename):
        print(f"الملف {local_filename} موجود بالفعل. سيتم تخطيه.")
        return local_filename

    try:
        with requests.get(url, stream=True, proxies=proxies) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            
            backup_file(local_filename)  # إنشاء نسخة احتياطية قبل الكتابة
            
            start_time = time.time()  # بدء التوقيت
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if progress_callback:
                        # تحديث التقدم
                        speed = downloaded_size / 1024 / (time.time() - start_time) if downloaded_size > 0 else 0
                        progress_callback(downloaded_size, total_size, speed)  # تحديث واجهة المستخدم

            # التحقق من سلامة الملف (يمكنك تعديلها حسب الحاجة)
            # expected_hash = "your_expected_hash_here"  # استخدم الـ hash المتوقع
            # if not verify_file_integrity(local_filename, expected_hash):
            #     print(f"سلامة الملف فشلت: {local_filename}")

    except Exception as e:
        print(f"فشل تنزيل {url}: {e}")

# وظيفة لتحليل الصفحة والحصول على أنواع الملفات المستهدفة
def get_target_files(base_url, response_text, file_types):
    soup = BeautifulSoup(response_text, 'html.parser')
    links = soup.find_all('a', href=True)
    target_files = [urljoin(base_url, link['href']) for link in links if link['href'].endswith(tuple(file_types))]
    return target_files

# وظيفة لتنزيل الملفات من صفحة الويب
def download_files(base_url, base_folder, proxies_list=None, file_types=None, progress_callback=None):
    os.makedirs(base_folder, exist_ok=True)
    proxies = None

    if proxies_list:
        valid_proxies = filter_valid_proxies(proxies_list)
        if not valid_proxies:
            return "فشلت جميع البروكسيات."
        proxies = {'http': valid_proxies[0], 'https': valid_proxies[0]}

    response = requests.get(base_url, proxies=proxies)
    target_files = get_target_files(base_url, response.text, file_types)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(download_file, urljoin(base_url, link), base_folder, proxies, progress_callback)
            for link in target_files
        ]
        for future in futures:
            future.result()  # تأكد من انتهاء جميع العمليات

    return f"تم تنزيل {len(target_files)} ملفات بنجاح."
