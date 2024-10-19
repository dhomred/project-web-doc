import os
import subprocess
import time
import requests




class VPNManager:
    def __init__(self, vpn_files, max_retries=3, retry_delay=5, country=None):
        self.vpn_files = vpn_files
        self.current_vpn_index = 0
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.country = country
        self.process = None  # حفظ العملية هنا لإغلاقها لاحقًا

    def connect_vpn(self, vpn_file):
        """الاتصال بخادم VPN باستخدام ملف OpenVPN."""
        try:
            # بدء عملية الاتصال بـ VPN
            self.process = subprocess.Popen(['openvpn', '--config', vpn_file],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(10)  # انتظار حتى يتم الاتصال

            if self.process.poll() is None:
                return True
            else:
                return False
        except Exception as e:
            print(f"فشل الاتصال بـ VPN: {e}")
            return False

    def disconnect_vpn(self):
        """فصل الاتصال بـ VPN."""
        if self.process:
            self.process.terminate()  # إنهاء العملية
            self.process = None
            print("تم فصل الاتصال بـ VPN.")
        else:
            print("لا يوجد اتصال بـ VPN لفصله.")
    
    def select_vpn_by_country(self):
        """اختيار VPN بناءً على الموقع الجغرافي."""
        if self.country:
            print(f"اختيار VPN للدولة: {self.country}")
            self.vpn_files = [vpn for vpn in self.vpn_files if self.country in vpn]
        else:
            print("لا توجد دولة محددة، سيتم استخدام قائمة VPN الافتراضية.")

    def test_dns_leak(self):
        """اختبار تسريبات DNS."""
        try:
            response = requests.get("https://dnsleaktest.com/json")
            dns_data = response.json()
            return dns_data
        except requests.RequestException as e:
            print(f"فشل في إجراء اختبار تسريب DNS: {e}")
            return None

    def connect_with_retry(self):
        """الاتصال بالـ VPN مع المحاولة المتكررة في حال الفشل."""
        self.select_vpn_by_country()
        for attempt in range(1, self.max_retries + 1):
            vpn_file = self.vpn_files[self.current_vpn_index]
            print(f"محاولة الاتصال بـ VPN: {vpn_file} (محاولة {attempt} من {self.max_retries})")
            if self.connect_vpn(vpn_file):
                print("تم الاتصال بـ VPN.")
                return True
            else:
                print(f"فشل الاتصال بـ VPN. إعادة المحاولة بعد {self.retry_delay} ثواني...")
                time.sleep(self.retry_delay)
        print("فشل الاتصال بجميع محاولات الـ VPN.")
        return False

    def get_current_location(self):
        """جلب الموقع الجغرافي الحالي."""
        try:
            response = requests.get("https://ipinfo.io")
            location_data = response.json()
            return location_data['country'], location_data['region'], location_data['city']
        except requests.RequestException as e:
            print(f"فشل في جلب الموقع: {e}")
            return None

def verify_vpn():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except:
        return False

# يمكنك إضافة بقية الكود هنا