import subprocess
import sys
import importlib

# قائمة بالمكتبات المطلوبة
required_libraries = [
    'requests',
    'beautifulsoup4',
    'tkinter',
    'threading',
    'concurrent.futures',
    'setuptools',
]

# وظيفة لتثبيت المكتبات المفقودة
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# التحقق من المكتبات وتثبيت المفقودة
def check_and_install_libraries(libraries):
    for library in libraries:
        try:
            importlib.import_module(library)
        except ImportError:
            print(f"{library} غير موجود، سيتم تثبيته...")
            install(library)

# بدء التطبيق
if __name__ == "__main__":
    check_and_install_libraries(required_libraries)

    # استيراد المكونات بعد التحقق من المكتبات
    from ui import create_ui
    from downloader import download_files
    from proxy import filter_valid_proxies_async
    from vpn import verify_vpn

    # يمكنك إضافة دالة هنا لتحديث الواجهة أو التقدم
    def progress_callback(downloaded_size, total_size, speed):
        # تحديث واجهة المستخدم بناءً على التقدم
        percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
        print(f"تم تنزيل {downloaded_size} من {total_size} بايت ({percentage:.2f}%) - السرعة: {speed:.2f} كيلوبايت/ثانية")

    # تمرير الدالة المحدثة إلى واجهة المستخدم
    create_ui(download_files, filter_valid_proxies_async, verify_vpn, progress_callback)
