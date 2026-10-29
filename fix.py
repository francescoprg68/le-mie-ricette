import sqlite3
conn = sqlite3.connect('ricettario.db')
c = conn.cursor()
for id, img in c.execute('SELECT id, immagine FROM ricette'):
    if img:
        new_img = img.replace('\\', '/')
        c.execute('UPDATE ricette SET immagine = ? WHERE id = ?', (new_img, id))
conn.commit()
conn.close()
print("Database aggiornato con successo!")
