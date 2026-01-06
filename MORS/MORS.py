import customtkinter as ctk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import os
from tkinter import filedialog

# إعدادات الواجهة الرسومية الفخمة
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MorsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MORS - Ultimate Automation")
        self.geometry("600x850")
        self.configure(fg_color="#080808")
        self.attached_file_path = "" 

        # الشعار العلوي
        self.logo = ctk.CTkLabel(self, text="MORS", font=ctk.CTkFont(size=65, weight="bold", family="Orbitron"))
        self.logo.pack(pady=(30, 5))
        
        self.status_msg = ctk.CTkLabel(self, text="NO LIMITS EDITION", text_color="#444", font=("Arial", 10, "bold"))
        self.status_msg.pack(pady=(0, 20))

        # حقول الإدخال
        self.sender_email = ctk.CTkEntry(self, placeholder_text="YOUR EMAIL (SENDER)", width=450, height=45, fg_color="#121212", border_color="#222")
        self.sender_email.pack(pady=8)

        self.app_password = ctk.CTkEntry(self, placeholder_text="APP PASSWORD", show="*", width=450, height=45, fg_color="#121212", border_color="#222")
        self.app_password.pack(pady=8)

        self.targets = ctk.CTkTextbox(self, width=450, height=130, fg_color="#121212", border_color="#222", text_color="#00FF7F")
        self.targets.insert("0.0", "TARGET EMAILS (LIST THEM HERE)")
        self.targets.pack(pady=8)

        self.message_body = ctk.CTkTextbox(self, width=450, height=150, fg_color="#121212", border_color="#222")
        self.message_body.insert("0.0", "MESSAGE BODY CONTENT...")
        self.message_body.pack(pady=8)

        # قسم المرفقات - يدعم كل الأنواع
        self.attach_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.attach_frame.pack(pady=15)

        self.btn_attach = ctk.CTkButton(self.attach_frame, text="ATTACH ANY FILE", command=self.upload_anything, 
                                       fg_color="#222", hover_color="#333", width=150)
        self.btn_attach.pack(side="left", padx=10)

        self.file_display = ctk.CTkLabel(self.attach_frame, text="READY TO ATTACH", text_color="#555")
        self.file_display.pack(side="left")

        # زر الإرسال الكبير
        self.send_btn = ctk.CTkButton(self, text="EXECUTE MISSION", command=self.launch_thread, 
                                     width=320, height=65, font=ctk.CTkFont(size=22, weight="bold"),
                                     fg_color="#1f538d", hover_color="#14375e", corner_radius=10)
        self.send_btn.pack(pady=25)

        # شريط الحالة السفلي
        self.status_bar = ctk.CTkLabel(self, text="SYSTEM ONLINE", text_color="#333", font=("Consolas", 12))
        self.status_bar.pack(side="bottom", pady=15)

    def upload_anything(self):
        # الآن الفلتر هو All Files (*.*)
        filename = filedialog.askopenfilename(title="Select Any File", filetypes=[("All Files", "*.*")])
        if filename:
            self.attached_file_path = filename
            file_size = round(os.path.getsize(filename) / (1024 * 1024), 2)
            self.file_display.configure(text=f"{os.path.basename(filename)} ({file_size} MB)", text_color="#00FF7F")

    def launch_thread(self):
        threading.Thread(target=self.send_logic, daemon=True).start()

    def send_logic(self):
        user = self.sender_email.get()
        pwd = self.app_password.get()
        list_emails = self.targets.get("1.0", "end-1c").strip().splitlines()
        content = self.message_body.get("1.0", "end-1c")

        if not user or not pwd or not list_emails:
            self.report("MISSING DATA!", "red")
            return

        try:
            self.report("INITIALIZING SERVER...", "#E1AD01")
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(user, pwd)

            for target in list_emails:
                target = target.strip()
                if target:
                    self.report(f"SENDING TO: {target}", "#00FF7F")
                    msg = MIMEMultipart()
                    msg['From'] = user
                    msg['To'] = target
                    msg['Subject'] = "Professional Application / Inquiry"
                    msg.attach(MIMEText(content, 'plain'))

                    # إرفاق الملف (مهما كان نوعه)
                    if self.attached_file_path:
                        with open(self.attached_file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attached_file_path)}")
                            msg.attach(part)
                    
                    session.send_message(msg)

            session.quit()
            self.report("ALL TARGETS REACHED SUCCESSFULLY!", "#00FF7F")
        except Exception as e:
            self.report(f"FAIL: {str(e)[:20]}...", "red")

    def report(self, text, color):
        self.status_bar.configure(text=f">> {text}", text_color=color)

if __name__ == "__main__":
    app = MorsApp()
    app.mainloop()