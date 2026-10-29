import sqlite3
conn = sqlite3.connect('ricettario.db')
c = conn.cursor()
c.execute('UPDATE ricette SET immagine = REPLACE(immagine, "\\", "/")')
conn.commit()
conn.close()
print("Aggiornato con successo")
