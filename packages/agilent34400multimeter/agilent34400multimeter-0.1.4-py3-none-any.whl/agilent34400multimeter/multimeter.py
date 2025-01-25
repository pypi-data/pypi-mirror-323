import pyvisa
import csv

# Ressourcen-Manager initialisieren
rm = pyvisa.ResourceManager()
global visaID 
visaID = 'USB0::0x0957::0x0618::TW48100045::0::INSTR' #insert your device ID from get_visa_id()


# Verfügbare Ressourcen auflisten
def get_visa_id():
    visaID = str(rm.list_resources())
    print('Your visaID is:', rm.list_resources())
    return visaID


# Verbindung zum Multimeter herstellen (ersetze die Adresse mit deiner tatsächlichen Adresse)
def make_connection(visaID):
    global multimeter
    multimeter = rm.open_resource(visaID)


# Geräte-Identifikation abfragen
def get_id():
    idn = multimeter.query('*IDN?')
    print(f"Geräte-ID: {idn}")


# Beispiel 1: Gleichspannungsmessung durchführen (DC Voltage)
def measure_dc_voltage():
    multimeter.write('MEAS:VOLT:DC?')
    voltage = float(multimeter.read())
    return voltage


# Beispiel 2: Wechselspannungsmessung durchführen (AC Voltage)
def measure_ac_voltage():
    multimeter.write('MEAS:VOLT:AC?')
    voltage = float(multimeter.read())
    return voltage


# Beispiel 3: DC-Strom messen
def measure_dc_current():
    multimeter.write('MEAS:CURR:DC?')
    current = float(multimeter.read())
    return current


# Beispiel 4: AC-Strom messen
def measure_ac_current():
    multimeter.write('MEAS:CURR:AC?')
    current = float(multimeter.read())
    return current


# Beispiel 5: Widerstand messen
def measure_resistance():
    multimeter.write('MEAS:RES?')
    resistance = float(multimeter.read())
    return resistance


# Beispiel 6: Frequenz messen
def measure_frequency():
    multimeter.write('MEAS:FREQ?')
    frequency = float(multimeter.read())
    return frequency    


# Beispiel 7: Anzeigeformat auf wissenschaftlich setzen (Scientific)
def set_display_format_scientific():
    multimeter.write('DISP:FORM SCI')
    print("Anzeigeformat auf wissenschaftlich gesetzt.")


# Beispiel 8: Anzeigeformat auf normal setzen
def set_display_format_normal():
    multimeter.write('DISP:FORM NORM')
    print("Anzeigeformat auf normal gesetzt.")


# Beispiel 9: Automatische Bereichswahl aktivieren
def enable_auto_range():
    multimeter.write('AUTO:RANG ON')
    print("Automatische Bereichswahl aktiviert.")


# Beispiel 10: Automatische Bereichswahl deaktivieren
def disable_auto_range():
    multimeter.write('AUTO:RANG OFF')
    print("Automatische Bereichswahl deaktiviert.")


# Beispiel 11: Diode messen (Diodentest)
def diode_test():
    multimeter.write('MEAS:DIOD?')
    diode_voltage = float(multimeter.read())
    return diode_voltage


# Beispiel 12: Kontinuitätstest durchführen (Piepston)
def continuity_test():
    multimeter.write('MEAS:CONT?')
    continuity = multimeter.read()
    if continuity == '1':
        print("Kontinuität: Durchgang (Piepston)")
    else:
        print("Kontinuität: Kein Durchgang")


# Beispiel 13: Messgerät in den Kalibrierungsmodus versetzen
def enter_calibration_mode():
    multimeter.write('CAL:ALL')
    print("Messgerät in den Kalibrierungsmodus versetzt.")


# Beispiel 14: Messgerät zurücksetzen
def reset_multimeter():
    multimeter.write('*RST')
    print("Messgerät zurückgesetzt.")


# Beispiel 15: Abfrage des Batteriestatus
def check_battery_status():
    multimeter.write('SYST:BAT?')
    battery_status = multimeter.read()
    print(f"Batteriestatus: {battery_status}")


# Beispiel 16: Ereignisprotokoll abfragen
def get_event_log():
    multimeter.write('EVEN:ALL?')
    event_log = multimeter.read()
    print(f"Ereignisprotokoll: {event_log}")


# Beispiel 17: Trigger-Modus einstellen (z.B. kontinuierlich)
def set_trigger_continuous():
    multimeter.write('TRIG:SOUR IMM')
    print("Trigger-Modus auf kontinuierlich gesetzt.")


# Beispiel 18: Trigger-Modus auf extern stellen
def set_trigger_external():
    multimeter.write('TRIG:SOUR EXT')
    print("Trigger-Modus auf extern gestellt.")


# Beispiel 19: Manuelle Bereichseinstellung für DC-Spannung
def set_dc_voltage_range():
    multimeter.write('VSET:VDC:FIX 10')  # Setzt den Bereich auf 10V DC
    print("Bereich für DC-Spannung auf 10V eingestellt.")


# Beispiel 20: Manuelle Bereichseinstellung für Widerstand
def set_resistance_range():
    multimeter.write('VSET:RES:FIX 100000')  # Setzt den Bereich für Widerstand auf 100k Ohm
    print("Bereich für Widerstand auf 100k Ohm eingestellt.")


# Beispiel 21: Oszilloskop-Modus aktivieren
def set_oscilloscope_mode():
    multimeter.write('SENS:VOLT:DC:ON')
    print("Oszilloskop-Modus aktiviert.")


# Beispiel 22: Messwiederholungen für kontinuierliche Messungen
def enable_continuous_measurement():
    multimeter.write('TRIG:SOUR IMM')  # Interner Trigger für kontinuierliche Messung
    multimeter.write('SAMP:COUN 1000')  # 1000 Messungen hintereinander
    print("Kontinuierliche Messung aktiviert.")


# Beispiel 23: Statistische Messungen (Min, Max, Durchschnitt)
def measure_statistics():
    multimeter.write('STAT:MODE MIN')
    min_value = multimeter.query('MEAS:VALL?')
    print(f"Minimale Messung: {min_value}")

    multimeter.write('STAT:MODE MAX')
    max_value = multimeter.query('MEAS:VALL?')
    print(f"Maximale Messung: {max_value}")

    multimeter.write('STAT:MODE AVG')
    avg_value = multimeter.query('MEAS:VALL?')
    print(f"Durchschnittliche Messung: {avg_value}")


# Beispiel 24: Trigger-Verzögerung einstellen
def set_trigger_delay():
    multimeter.write('TRIG:DLY 0.5')  # Verzögerung auf 0.5 Sekunden setzen
    print("Trigger-Verzögerung auf 0.5 Sekunden eingestellt.")


# Beispiel 25: USB-Schnittstelle zurücksetzen
def reset_usb_interface():
    multimeter.write('SYST:USB:RESET')  # Setzt die USB-Schnittstelle zurück
    print("USB-Schnittstelle zurückgesetzt.")


# Beispiel 26: Temperaturmessung (Thermoelement)
def measure_temperature():
    multimeter.write('MEAS:TEMP?')  # Temperaturmessung starten
    temperature = float(multimeter.read())
    return temperature


# Beispiel 27: Stromversorgung des Geräts steuern (Ein/Aus)
def turn_on_multimeter():
    multimeter.write('SYSTEM:POWER ON')
    print("Multimeter eingeschaltet.")


def turn_off_multimeter():
    multimeter.write('SYSTEM:POWER OFF')
    print("Multimeter ausgeschaltet.")


# Beispiel 28: Automatische Kalibrierung durchführen
def auto_calibrate():
    multimeter.write('CAL:ALL')  # Alle Kalibrierungen durchführen
    print("Automatische Kalibrierung durchgeführt.")


# Beispiel 29: Grenzwert für Messungen setzen
def set_measurement_limits():
    multimeter.write('MEAS:LIM:VOLT:DC 10')  # Grenzwert für DC-Spannung auf 10V setzen
    print("Grenzwert für DC-Spannung auf 10V gesetzt.")


# Beispiel 30: Mehrere Messwerte gleichzeitig abfragen
def measure_multiple_values():
    multimeter.write('MEAS:VOLT:DC?')
    voltage = float(multimeter.read())
    multimeter.write('MEAS:RES?')
    resistance = float(multimeter.read())
    return voltage, resistance


# Beispiel 31: Messdaten in CSV-Datei protokollieren
def log_data_to_csv():
    voltage = measure_dc_voltage()  # Messung durchführen
    resistance = measure_resistance()
    with open('measurement_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([voltage, resistance])
    print("Messdaten wurden in 'measurement_log.csv' protokolliert.")


# Beispiel 32: Externe Triggerquelle aktivieren
def set_external_trigger():
    multimeter.write('TRIG:SOUR EXT')  # Setzt den Trigger-Modus auf extern
    print("Externer Trigger-Modus aktiviert.")


# Beispiel 33: Transistor messen
def test_transistor():
    multimeter.write('MEAS:VBE?')  # Messung der Basis-Emitter-Spannung eines Transistors
    voltage = float(multimeter.read())
    return voltage


# Beispiel 34: Kapazität messen
def measure_capacitance():
    multimeter.write('MEAS:CAP?')
    capacitance = float(multimeter.read())
    return capacitance


# Beispiel 35: Impedanz messen
def measure_impedance():
    multimeter.write('MEAS:IMP?')
    impedance = float(multimeter.read())
    return impedance


# Beispiel 36: Kalibrierstatus abfragen
def check_calibration_status():
    multimeter.write('CAL:STAT?')  # Abfrage des Kalibrierstatus
    status = multimeter.read()
    print(f"Kalibrierstatus: {status}")


# Beispiel 37: Messmodus (Auto/Manuell) wechseln
def set_manual_mode():
    multimeter.write('MEAS:MODE MAN')
    print("Manuellen Modus eingestellt.")


def set_auto_mode():
    multimeter.write('MEAS:MODE AUTO')
    print("Automatischen Modus eingestellt.")


# Beispiel 38: Vierdrahtmessung für Widerstand aktivieren
def set_four_wire_resistance():
    multimeter.write('SENS:RES:MODE 4WIRE')  # Aktiviert den Vierdrahtmodus für Widerstandsmessung
    print("Vierdrahtmessung für Widerstand aktiviert.")


# Beispiel 39: Zweidrahtmessung für Widerstand aktivieren
def set_two_wire_resistance():
    multimeter.write('SENS:RES:MODE 2WIRE')  # Aktiviert den Zweidrahtmodus für Widerstandsmessung
    print("Zweidrahtmessung für Widerstand aktiviert.")


# Beispiel 40: Anzeigehelligkeit anpassen
def adjust_display_brightness(brightness_level):
    multimeter.write(f'DISP:BRIG {brightness_level}')  # Helligkeit der Anzeige anpassen (1 bis 10)
    print(f"Anzeigehelligkeit auf {brightness_level} gesetzt.")


# Beispiel 41: Anzahl der angezeigten Ziffern anpassen
def set_display_digits(digits):
    multimeter.write(f'DISP:DIG {digits}')  # Anzahl der angezeigten Ziffern anpassen
    print(f"Anzeige auf {digits} Ziffern eingestellt.")


# Beispiel 42: Weitere Messungen durchführen
def multi_measurement_sequence():
    for i in range(5):  # Führe 5 Messungen durch
        print(f"Messung {i+1}:")
        measure_dc_voltage()
        measure_resistance()
        measure_ac_voltage()


# Beispiel 43: Höchste Präzision aktivieren
def set_high_precision():
    multimeter.write('SENS:VOLT:DC:RESO MAX')  # Höchste Auflösung für DC-Spannung
    multimeter.write('SENS:RES:RESO MAX')  # Höchste Auflösung für Widerstand
    print("Höchste Präzision für Messungen aktiviert.")


# Beispiel 44: Ereignis-Trigger aktivieren
def enable_event_trigger():
    multimeter.write('SYST:EVEN:ENAB ON')  # Aktiviert Ereignis-Trigger
    print("Ereignis-Trigger aktiviert.")


# Beispiel 45: Alarmstatus abfragen
def check_for_alarms():
    multimeter.write('SYST:EVEN:STAT?')
    status = multimeter.read()
    print(f"Alarmstatus: {status}")
