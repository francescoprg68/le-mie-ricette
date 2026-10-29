import sqlite3
conn = sqlite3.connect('ricettario.db')
c = conn.cursor()
c.execute("UPDATE ricette SET immagine = REPLACE(immagine, 'D:\\CUCINA\\media_cucina\\', 'media_cucina/')")
c.execute("UPDATE ricette SET immagine = REPLACE(immagine, '\\', '/')")
conn.commit()
conn.close()
print("Percorsi corretti con successo!")
