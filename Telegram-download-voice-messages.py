from telethon import TelegramClient, events, sync
from telethon.tl.types import InputMessagesFilterRoundVoice  # Filter (z.B. Sprachnachricht, Photos, usw. siehe https://tl.telethon.dev/constructors/index.html)
import os.path
#from os.path import exists
import logging

'''
Notice:
This program uses the Telegram API and is part of the Telegram ecosystem.
'''

# Parameter:
folder = r"f:\path\to\your\targetfolder"  # The folder where your files and the ID repository file are to be saved.
channel = "channelname"  # Type here in the channel's name. The full link  https://t.me/channelname probably works too.
limit = 100  # value which indicates how many files you want to download, set it to <None> for no limit
api_id = 1234567  # get your api_id from https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
api_hash = 'tpyeHereYourAPI-hash'  # get your api_hash from https://core.telegram.org/api/obtaining_api_id#obtaining-api-id

os.chdir(folder)  # Arbeitsverzeichnis zum Zielordner ändern
logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)

client = TelegramClient('session_name', api_id, api_hash)
print("Starte Client")
client.start()
logging.info("Client gestartet")

print("Einträge einholen")
msgs = client.get_messages(entity=channel, limit=limit, filter=InputMessagesFilterRoundVoice)
print(len(msgs), "Einträge vorhanden")

errlist = []  # Nicht heruntergeladene message-Namen
skipped = []  # Nicht heruntergeladene message-Namen
counter = 0  # Zähler wieviele Nachrichten übrig sind
counter_unknown = 0  # Zähler wieviele Nachrichten übrig sind

# Establishing list of voice message IDs to prevent downloading duplicates
id_rep_file = open('id_list.txt', 'a')  # Liste mit gespeicherten IDs, a+ für erstellen bei Bedarf, lesen + schreiben
id_rep = id_rep_file.read().splitlines()  # id repository
id_container = []  # Liste mit IDs, die nun von Telegram abgefragt werden

for msg in msgs:  # IDs sammeln
    id_container.append(msg.file.id)
    # id_list_lines.append(msg.file.id)  # zusammengefügte Liste mit vorhandenen IDs und jenen von Telegram

# missingidlist = [item for item in id_list_lines if item not in id_container]  # Alternativer Ausdruck
# missingidlist = set(id_list_lines)  #  Alle IDs löschen, die nun doppelt vorhanden sind: Jene Dateien fehlen und sind herunterzuladen
missingidlist = list(set(id_container).difference(id_rep))  # Ausfiltern von doppelter Einträge aus den zwei Listen. Resultat sind die herunterzuladenen Dateien.

for msg in msgs:
    counter += 1

    file_id = msg.file.id
    titel = msg.text  # oder möglich: msg.message
    if any(file_id in s for s in missingidlist):  # Datei ist noch nicht vorhanden, also herunterladen

        endung = msg.file.ext
        creatime = msg.date.date().isoformat()  # Datumsformat: yyyy-mm-dd
        views = msg.views  # views speichern
        views = round(views / 100) * 100  # Auf hunderter runden
        views = str(views)  # in Text konvertieren

        if titel:  # oder möglich: msg.message
            filename = creatime + " " + titel + " " + views + "views" + endung  # Name + Dateiendung
        else:
            filename = creatime + " unknown" + str(counter_unknown) + " " + views + "views" + endung
            counter_unknown += 1

        # Unerlaubte Dateizeichen ersetzen
        filename = filename.replace("\n", " - ")  # "\n" ersetzen mit Bindestrich
        filename = filename.replace("\\", "-")  # "n" ersetzen mit Bindestrich
        filename = filename.replace("/", "-")   # "/" ersetzen mit Bindestrich
        filename = filename.replace("?", "-")   # "/" ersetzen mit Bindestrich
        filename = filename.replace("\"", "!")   # "/" ersetzen mit Bindestrich
        filename = filename.replace(r"*", " ! ")   # "/" ersetzen mit Bindestrich
        filename = filename.replace(r"<", " ! ")   # "/" ersetzen mit Bindestrich
        filename = filename.replace(r">", " ! ")   # "/" ersetzen mit Bindestrich
        filename = filename.replace(r":", " - ")   # "/" ersetzen mit Bindestrich

        try:  # Datei ist noch nicht im Verzeichnis. Versuchen, sie herunterzuladen
            print("Herunterladen von Nr.", counter, "von", len(msgs) - counter, "\n", filename, "File ID:", msg.file.id)
            msg.download_media(filename)
            print("msg:", filename, "runtergeladen")
            # print(len(msgs) - counter, " übrig", "\n")
            # id_list.append(msg.id)  # Erfolgreiche Message-ID in Liste speichern
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,
            # print ("msg:\n", filename, "\nkonnte nicht heruntergeladen werden")
            logging.info("msg:", filename, "ID:", file_id, "konnte nicht heruntergeladen werden\n")
            errlist.append(filename)

        id_rep_file.write(file_id+"\n")  # heruntergeladene ID einpflegen

    else:  # Datei ist vorhanden, also nicht herunterladen:
        logging.debug("Überspringe Titel: %s, ID: %s" % (titel, file_id))

        print(len(msgs) - counter, " übrig", "\n")
        skipped.append(titel)  # Liste füllen übersprungener Dateien
        skipped.append(file_id)  # Liste füllen übersprungener Dateien

id_rep_file.close()
client.disconnect()

errlist_string = "\n".join(errlist)  # Konvertierung in einen String für Logger
skipped_string = "\n".join(skipped)  # Konvertierung in einen String für Logger

# print("Einträge runterladen abgeschlossen\n")
logging.info("\nEinträge runterladen abgeschlossen")
# print("Konnten nicht heruntergeladen werden:", errlist, "\n")
logging.info("Konnten nicht heruntergeladen werden:\n + %s" % errlist_string)
# print("Anzahl übersprungener Dateien:", len(skipped), "\n", "Dateien:", skipped)
logging.info("Übersprungene Dateien:\n %s" % skipped_string)

# os.system("shutdown -s -t 10")  # Computer herunterfahren, letzte Zahl ist Timer in Sekunden
