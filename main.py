import urllib.parse
import requests
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label

class KrnApp(App):
    def build(self):
        self.title = "krn"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.chat = Label(
            text="[b]krn Süper İnternet Asistanı Hazır![/b]\n• Haber, Dolar, Hava Durumu sorabilirsin.\n• Her türlü genel bilgi için arama yapabilirsin.\n" + "-"*35 + "\n",
            size_hint_y=None,
            markup=True,
            halign='left'
        )
        self.chat.bind(texture_size=self.chat.setter('size'))
        self.scroll.add_widget(self.chat)
        
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=5)
        self.user_input = TextInput(hint_text="krn'e bir şey sor...", multiline=False)
        btn = Button(text="Gönder", size_hint=(0.3, 1))
        btn.bind(on_press=self.send_msg)
        
        input_layout.add_widget(self.user_input)
        input_layout.add_widget(btn)
        
        layout.add_widget(self.scroll)
        layout.add_widget(input_layout)
        return layout

    def get_crypto_currency(self):
        try:
            res = requests.get("https://api.genelpara.com/embed/doviz.json", timeout=3).json()
            usd = res.get("USD", {}).get("satis", "N/A")
            eur = res.get("EUR", {}).get("satis", "N/A")
            return f"💵 **Dolar:** {usd} TL | 💶 **Euro:** {eur} TL"
        except:
            return "Piyasa verileri şu an alınamadı."

    def get_weather(self, city="Bursa"):
        try:
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C+%t+%w&lang=tr"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                return f"🌤️ **{city.capitalize()} Hava Durumu:** {res.text.strip()}"
            return "Hava durumu bilgisi alınamadı."
        except:
            return "Hava durumu servisine bağlanılamadı."

    def web_search_deep(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            res = requests.get(url, timeout=3).json()
            if res.get("AbstractText"):
                return res["AbstractText"]
            elif res.get("RelatedTopics"):
                for topic in res["RelatedTopics"]:
                    if "Text" in topic:
                        return topic["Text"]
        except:
            pass

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.DOTALL)
                if snippets:
                    clean_text = re.sub(r'<[^>]+>', '', snippets[0]).strip()
                    return clean_text
        except:
            pass

        return None

    def fetch_news(self):
        try:
            url = "https://newsdata.io/api/1/news?apikey=pub_66030c6a51d4d8a57ba8d61e1fa42cd8e412d&country=tr&language=tr"
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                results = res.json().get("results", [])
                if results:
                    news_text = "[b]📰 Son Haberler:[/b]\n"
                    for item in results[:3]:
                        news_text += f"• {item.get('title', 'Başlıksız Haber')}\n"
                    return news_text
            return "Haberler şu an çekilemedi."
        except:
            return "Haber servisine bağlanılamadı."

    def send_msg(self, instance):
        txt = self.user_input.text.strip()
        if not txt:
            return
            
        self.chat.text += f"\n[b]Sen:[/b] {txt}\n"
        self.user_input.text = ""
        txt_lower = txt.lower()

        if txt_lower in ["selam", "merhaba", "sa", "selamün aleyküm"]:
            ans = "Aleykümselam! Tüm canlı internet modülleri aktif. Ne bakmamı istersin?"
        elif txt_lower in ["nasılsın", "nasılsın?", "naber"]:
            ans = "Harikayım! Sistemlerim açık, aramaya hazırım."
        elif any(k in txt_lower for k in ["dolar", "euro", "döviz", "piyasa"]):
            ans = self.get_crypto_currency()
        elif "hava" in txt_lower:
            city = txt_lower.replace("hava", "").replace("durumu", "").replace("kaç", "").replace("derece", "").strip()
            city = city if city else "Bursa"
            ans = self.get_weather(city)
        elif "haber" in txt_lower:
            ans = self.fetch_news()
        else:
            ans_wiki = None
            try:
                res = requests.get(
                    f"https://tr.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(txt)}",
                    timeout=3
                )
                if res.status_code == 200:
                    ans_wiki = res.json().get("extract")
            except:
                pass

            if ans_wiki:
                ans = ans_wiki
            else:
                web_res = self.web_search_deep(txt)
                if web_res:
                    ans = f"[🌐 İnternet Arama Sonucu]:\n{web_res}"
                else:
                    ans = f"'{txt}' hakkında internette net bir özet bulunamadı. Lütfen kelimeleri biraz daha açık yaz."

        self.chat.text += f"[b]krn:[/b] {ans}\n" + "-"*35 + "\n"

if __name__ == '__main__':
    KrnApp().run()
