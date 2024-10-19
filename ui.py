import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import scrolledtext
import threading  # لإدارة الخيوط

class DownloaderUI:
    def __init__(self, master, download_function, filter_proxies_function, verify_vpn_function):
        self.master = master
        self.download_function = download_function
        self.filter_proxies_function = filter_proxies_function
        self.verify_vpn_function = verify_vpn_function

        self.master.title("Downloader App")
        self.master.geometry("600x700")

        # إطار لإدخال البيانات
        self.frame = ttk.Frame(self.master)
        self.frame.pack(pady=10)

        # إدخال URL
        ttk.Label(self.frame, text="ادخل رابط الصفحة:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(self.frame, width=50)
        self.url_entry.grid(row=0, column=1)

        # إدخال مسار المجلد
        ttk.Label(self.frame, text="مسار المجلد:").grid(row=1, column=0, sticky=tk.W)
        self.folder_entry = ttk.Entry(self.frame, width=50)
        self.folder_entry.grid(row=1, column=1)
        ttk.Button(self.frame, text="تصفح", command=self.browse_folder).grid(row=1, column=2)

        # إدخال صيغة الملفات
        ttk.Label(self.frame, text="أدخل صيغ الملفات (مثل .pdf, .jpg):").grid(row=2, column=0, sticky=tk.W)
        self.file_types_entry = ttk.Entry(self.frame, width=50)
        self.file_types_entry.grid(row=2, column=1)

        # قائمة Checkboxes لأنواع الملفات
        self.file_types = ['.pdf', '.jpg', '.png', '.txt', '.docx']
        self.file_vars = {file_type: tk.IntVar(value=0) for file_type in self.file_types}
        
        ttk.Label(self.frame, text="اختر أنواع الملفات:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        for index, file_type in enumerate(self.file_types):
            ttk.Checkbutton(self.frame, text=file_type, variable=self.file_vars[file_type]).grid(row=4 + index, column=0, sticky=tk.W)

        # Checkboxes للبروكسي وVPN
        self.proxy_var = tk.IntVar(value=0)
        self.vpn_var = tk.IntVar(value=0)

        ttk.Checkbutton(self.frame, text="استخدام البروكسي", variable=self.proxy_var, command=self.toggle_proxy_input).grid(row=9, column=0, sticky=tk.W)
        ttk.Checkbutton(self.frame, text="استخدام VPN", variable=self.vpn_var, command=self.toggle_vpn_input).grid(row=9, column=1, sticky=tk.W)

        # اختيار نوع البروكسي (HTTP, SOCKS4, SOCKS5)
        self.proxy_type = tk.StringVar(value='http')
        ttk.Label(self.frame, text="نوع البروكسي:").grid(row=10, column=0, sticky=tk.W)
        self.proxy_type_menu = ttk.OptionMenu(self.frame, self.proxy_type, 'http', 'http', 'socks4', 'socks5')
        self.proxy_type_menu.grid(row=10, column=1, sticky=tk.W)

        # زر لاختيار ملف البروكسي
        ttk.Label(self.frame, text="ملف البروكسي:").grid(row=11, column=0, sticky=tk.W)
        self.proxy_file_entry = ttk.Entry(self.frame, width=50)
        self.proxy_file_entry.grid(row=11, column=1)
        ttk.Button(self.frame, text="تصفح بروكسي", command=self.browse_proxy_file).grid(row=11, column=2)

        # زر لاختيار ملف VPN
        ttk.Label(self.frame, text="ملف VPN:").grid(row=12, column=0, sticky=tk.W)
        self.vpn_file_entry = ttk.Entry(self.frame, width=50)
        self.vpn_file_entry.grid(row=12, column=1)
        ttk.Button(self.frame, text="تصفح VPN", command=self.browse_vpn_file).grid(row=12, column=2)

        # زر بدء التنزيل
        self.download_button = ttk.Button(self.frame, text="بدء التنزيل", command=self.start_download)
        self.download_button.grid(row=13, column=0, columnspan=2, pady=10)

        # منطقة عرض الحالة
        self.status_text = scrolledtext.ScrolledText(self.master, width=70, height=10, state='disabled')
        self.status_text.pack(pady=10)

        # منطقة عرض حالة التنزيل
        self.download_status = tk.StringVar()
        self.download_status_label = ttk.Label(self.master, textvariable=self.download_status)
        self.download_status_label.pack(pady=5)

        # منطقة عرض عنوان IP
        self.ip_status = tk.StringVar()
        self.ip_status_label = ttk.Label(self.master, textvariable=self.ip_status)
        self.ip_status_label.pack(pady=5)

        # مؤشرات التحميل
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10)

        # منطقة عرض معلومات التحميل
        self.download_info = tk.StringVar()
        self.download_info_label = ttk.Label(self.master, textvariable=self.download_info)
        self.download_info_label.pack(pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def browse_proxy_file(self):
        proxy_file_selected = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if proxy_file_selected:
            self.proxy_file_entry.delete(0, tk.END)
            self.proxy_file_entry.insert(0, proxy_file_selected)

    def browse_vpn_file(self):
        vpn_file_selected = filedialog.askopenfilename(filetypes=[("VPN Files", "*.ovpn")])
        if vpn_file_selected:
            self.vpn_file_entry.delete(0, tk.END)
            self.vpn_file_entry.insert(0, vpn_file_selected)

    def toggle_proxy_input(self):
        if self.proxy_var.get() == 0:
            self.proxy_file_entry.config(state='disabled')
        else:
            self.proxy_file_entry.config(state='normal')

    def toggle_vpn_input(self):
        if self.vpn_var.get() == 0:
            self.vpn_file_entry.config(state='disabled')
        else:
            self.vpn_file_entry.config(state='normal')

    def start_download(self):
        url = self.url_entry.get()
        folder = self.folder_entry.get()
        file_types = [ft for ft, var in self.file_vars.items() if var.get() == 1]
        proxy_file = self.proxy_file_entry.get() if self.proxy_var.get() else None
        vpn_file = self.vpn_file_entry.get() if self.vpn_var.get() else None
        proxy_type = self.proxy_type.get()  # الحصول على نوع البروكسي المختار

        if not url or not folder or not file_types:
            messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول.")
            return

        # تحذير المستخدم قبل بدء التحميل
        if self.proxy_var.get() == 1 and not proxy_file:
            messagebox.showwarning("تحذير", "يرجى تحديد ملف البروكسي عند استخدام البروكسي.")
            return

        if self.vpn_var.get() == 1 and not vpn_file:
            messagebox.showwarning("تحذير", "يرجى تحديد ملف VPN عند استخدام VPN.")
            return

        # بدء عملية التحميل في خيط منفصل
        download_thread = threading.Thread(target=self.run_download, args=(url, folder, proxy_file, file_types, vpn_file, proxy_type))
        download_thread.start()

    def run_download(self, url, folder, proxy_file, file_types, vpn_file, proxy_type):
        # بدء الاتصال بـ VPN إذا تم تحديده
        if self.vpn_var.get() and vpn_file:
            self.verify_vpn_function(vpn_file)

        # تحديث حالة التنزيل
        self.download_status.set("جاري تنزيل الملفات...")
        
        # استدعاء دالة التنزيل وتحديث الحالة بناءً على النتائج
        result = self.download_function(url, folder, [proxy_file], file_types, self.update_progress)

        # تحديث معلومات التحميل
        self.download_info.set(result)

    def update_progress(self, downloaded_size, total_size, speed):
        percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
        self.progress_var.set(percentage)
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"تم تنزيل {downloaded_size} من {total_size} بايت ({percentage:.2f}%) - السرعة: {speed:.2f} كيلوبايت/ثانية\n")
        self.status_text.config(state='disabled')
        self.status_text.yview(tk.END)  # Scroll to the end

# استدعاء create_ui مع المعلمات الصحيحة
def create_ui(download_function, filter_proxies_function, verify_vpn_function,  progress_callback):
    root = tk.Tk()
    app = DownloaderUI(root, download_function, filter_proxies_function, verify_vpn_function,)
    root.mainloop()

