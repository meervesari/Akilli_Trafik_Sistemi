import os
import sys
import traci

# 1. Ortam Değişkeni Kontrolü
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Hata: SUMO_HOME ayarlı değil!")

def run_simulation():
    # '--delay 400' yaparak simülasyonu iyice yavaşlattık (daha anlaşılır olması için)
    sumo_cmd = ["sumo-gui", "-c", "../simulation/kavsak.sumocfg", "--start", "--delay", "400"]
    traci.start(sumo_cmd)

    min_yesil_sure = 20  # Bir ışık en az 20 adım boyunca yeşil kalacak
    son_degisim_adimi = 0
    su_anki_faz = 0

    print("\n--- Akıllı Kontrol Başladı ---")

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            sim_zaman = traci.simulation.getTime()
            
            # Şeritlerdeki araç sayılarını oku
            k = traci.lane.getLastStepVehicleNumber("kuzey_0")
            g = traci.lane.getLastStepVehicleNumber("guney_0")
            d = traci.lane.getLastStepVehicleNumber("dogu_0")
            b = traci.lane.getLastStepVehicleNumber("bati_0")

            dikey_yogunluk = k + g
            yatay_yogunluk = d + b

            # ANLAŞILIR MANTIK: Sadece minimum süre dolduğunda karar değiştir
            if (sim_zaman - son_degisim_adimi) >= min_yesil_sure:
                
                eski_faz = su_anki_faz
                
                if dikey_yogunluk > yatay_yogunluk:
                    su_anki_faz = 0 # Kuzey-Güney Yeşil
                elif yatay_yogunluk > dikey_yogunluk:
                    su_anki_faz = 2 # Doğu-Batı Yeşil

                # Eğer yapay zeka fazı değiştirmeye karar verdiyse komutu gönder
                if su_anki_faz != eski_faz:
                    traci.trafficlight.setPhase("0", su_anki_faz)
                    son_degisim_adimi = sim_zaman
                    yön = "DİKEY (Kuzey-Güney)" if su_anki_faz == 0 else "YATAY (Doğu-Batı)"
                    print(f"Zaman: {sim_zaman} | Yapay Zeka Kararı: Yoğunluk nedeniyle {yön} aksına geçildi.")

            if sim_zaman > 200:
                break
                
    finally:
        traci.close()
        print("Simülasyon anlaşılır şekilde tamamlandı.")

if __name__ == "__main__":
    run_simulation()