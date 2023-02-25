import psycopg2


class UseDB:

    def __init__(self, db, user, password):
        self.db = db
        self.user = user
        self.password = password

    def _connect_db(self):
        connect = psycopg2.connect(database=self.db, user=self.user, password=self.password)
        return connect

    def create_tables(self):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS clients(
                        cli_id SERIAL PRIMARY KEY,
                        first_name VARCHAR(40),
                        last_name VARCHAR(40));""")
            cur.execute("""CREATE TABLE IF NOT EXISTS contacts(
                        cont_id SERIAL PRIMARY KEY,
                        number VARCHAR(40) NOT NULL UNIQUE,
                        email VARCHAR(40));""")
            cur.execute("""CREATE TABLE IF NOT EXISTS cli_cont(
                        id SERIAL PRIMARY KEY,
                        cli_id INT REFERENCES clients(cli_id) ON DELETE CASCADE,
                        cont_id INT REFERENCES contacts(cont_id) ON DELETE CASCADE);""")
            connect.commit()
        connect.close()
        return

    def new_user_create(self, fn, ln, pn=None, em=None):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""INSERT INTO clients(first_name, last_name) VALUES(%s, %s) RETURNING cli_id;""", (fn, ln))
            cli_id = cur.fetchone()
            cur.execute("""INSERT INTO contacts(number, email) VALUES(%s, %s) RETURNING cont_id;""", (pn, em))
            cont_id = cur.fetchone()
            cur.execute("""INSERT INTO cli_cont(cli_id, cont_id) VALUES( %s, %s);""", (cli_id, cont_id))
            connect.commit()
        connect.close()
        return

    def add_number(self, fn, ln, pn=None, em=None):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""SELECT c.cli_id FROM clients c WHERE c.first_name = %s AND c.last_name = %s;""", (fn, ln))
            cli_id = cur.fetchone()
            cur.execute("""INSERT INTO contacts(number, email) VALUES(%s, %s) RETURNING cont_id;""", (pn, em))
            cont_id = cur.fetchone()
            cur.execute("""INSERT INTO cli_cont(cli_id, cont_id) VALUES( %s, %s);""", (cli_id, cont_id))
            connect.commit()
        connect.close()
        return

    def update_number(self, old_pn, new_pn):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""SELECT c.cont_id FROM contacts as c WHERE c.number = %s;""", (old_pn,))
            flag = cur.fetchone()
            if flag:
                cur.execute("""UPDATE contacts SET number = %s WHERE number = %s;""", (new_pn, old_pn))
            else:
                print('Номер указанный для исправления не найден.')
            connect.commit()
        connect.close()
        return

    def update_email(self, old_em, new_em):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""SELECT c.cont_id FROM contacts as c WHERE c.email = %s;""", (old_em,))
            flag = cur.fetchone()
            if flag:
                cur.execute("""UPDATE contacts SET email = %s WHERE email = %s;""", (new_em, old_em))
            else:
                print('Email указанный для исправления не найден.')
            connect.commit()
        connect.close()
        return

    def del_number(self, fn, ln):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""
                    SELECT c.cli_id FROM clients c WHERE c.first_name = %s AND c.last_name = %s;""", (fn, ln))
            cli_id = cur.fetchone()
            cur.execute(
                """SELECT cc.cont_id FROM cli_cont cc WHERE cc.cli_id = %s;""", (cli_id,))
            id_list = cur.fetchall()
            for c_id in id_list:
                cur.execute("""DELETE FROM contacts c WHERE c.cont_id = %s;""", c_id)
            connect.commit()
        connect.close()
        return

    def del_user(self, fn, ln):
        connect = self._connect_db()
        with connect.cursor() as cur:
            cur.execute("""
                    SELECT c.cli_id FROM clients c WHERE c.first_name = %s AND c.last_name = %s;""", (fn, ln))
            cli_id = cur.fetchone()
            self.del_number(fn, ln)
            cur.execute("""DELETE FROM clients c WHERE c.cli _id = %s;""", cli_id)
            connect.commit()
        connect.close()
        return

    def search_client(self, fn=None, ln=None, pn=None, em=None):
        connect = self._connect_db()
        with connect.cursor() as cur:
            if fn and ln:
                cur.execute("""SELECT c2.number, c2.email  FROM clients c 
                                join cli_cont cc on c.cli_id = cc.cli_id 
                                join contacts c2 on cc.cont_id = c2.cont_id 
                                where c.first_name = %s and c.last_name = %s;""", (fn, ln))
                data_list = cur.fetchall()
                print(f'Для пользователя {fn} {ln} найдены следующие данные:')
                counter = 1
                for phone, email in data_list:
                    print(f'Телефон №{counter}: {phone}. Email №{counter}: {email}')
                    counter += 1
            elif pn:
                cur.execute("""SELECT c.first_name, c.last_name FROM clients c 
                            join cli_cont cc on c.cli_id = cc.cli_id 
                            join contacts c2 on cc.cont_id = c2.cont_id 
                            where c2.number = %s;""", (pn,))
                fname, lname = cur.fetchone()
                print(f"Указанный телефон принадлежит {fname} {lname}.")
            elif em:
                cur.execute("""SELECT c.first_name, c.last_name FROM clients c 
                            join cli_cont cc on c.cli_id = cc.cli_id 
                            join contacts c2 on cc.cont_id = c2.cont_id 
                            where c2.email = %s;""", (em,))
                fname, lname = cur.fetchone()
                print(f"Указанный email принадлежит {fname} {lname}.")


if __name__ == '__main__':
    cli_db = UseDB("______", "______", "______")
    # cli_db.create_tables()
    # cli_db.new_user_create('Ilya', 'Pavlov', '123456789', 'xxx@yyy.com')
    # cli_db.new_user_create('Den', 'Fadeev', '987654321', 'yyy@xxx.com')
    # cli_db.add_number('Ilya', 'Pavlov', '111111111', '')
    # cli_db.update_number('123456789', '777777777')
    # cli_db.update_email('yyy@xxx.com', 'client@new.com')
    # cli_db.del_number('Ilya', 'Pavlov')
    # cli_db.del_user('Den', 'Fadeev')
    # cli_db.search_client('Ilya', 'Pavlov')
    # cli_db.search_client(pn="123456789")
    # cli_db.search_client(em="yyy@xxx.com")
