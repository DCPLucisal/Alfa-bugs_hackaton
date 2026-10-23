import backend.database.db as db
import bcrypt
from psycopg2.extras import RealDictCursor

def get_client(email : str, password : str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT c.id, c.name, c.lastname, c.middlename, c.phone_number, c.email
            FROM clients c
            WHERE c.email = %s
                  AND c.password = %s
            """, (email, password))
            row = cur.fetchone()
            return row
        
def get_client_by_id(id: int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT c.id, c.name, c.lastname, c.middlename, c.phone_number, c.email
            FROM clients c
            WHERE c.id = %s
            """, (id,))
            row = cur.fetchone()
            return row

def get_company_data(inn: str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT e.bki_data, e.fns_data, e.fetched_at,
            FROM externaldata e
            JOIN companies c ON c.id = e.company_id
            WHERE c.inn = %s
            ORDER BY e.fetched_at DESC
            LIMIT 1
            """, (inn,))
            row = cur.fetchone()    
            if row is None:
                return None
            return row

def get_applications_for_analysis():
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.id,cl.name, cl.lastname, cl.middlename, cl.phone_number,cl.email,
                   co.inn, a.application_type,a.amount, a.term_value, 
                   a.term_unit, a.aim, a.status, a.created, a.updated,
                   sr.risk_category
            FROM applications a
            JOIN clients cl on cl.id = a.client_id
            JOIN companies co on co.id = a.company_id
            JOIN scoringresults sr on sr.application_id = a.id
            WHERE a.status <> 'draft'
            """)
            row = cur.fetchall()
            return row
        
def get_users_applications(client_id: int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.id,cl.name, cl.lastname, cl.middlename, cl.phone_number,cl.email,
                   co.inn, a.application_type,a.amount, a.term_value, 
                   a.term_unit, a.aim, a.status, a.created, a.updated,
                   sr.risk_category
            FROM applications a
            JOIN clients cl on cl.id = a.client_id
            JOIN companies co on co.id = a.company_id
            LEFT JOIN scoringresults sr on sr.application_id = a.id
            WHERE a.client_id = %s
            """, (client_id,))
            row = cur.fetchall()
            return row
        
def get_application_by_id(id: int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                cl.name AS client_name, 
                cl.lastname AS client_lastname, 
                cl.middlename AS client_middlename, 
                cl.email, 
                cl.phone_number,
                
                co.inn, 
                a.id AS application_id,
                a.application_type, 
                a.amount, 
                a.term_value, 
                a.term_unit, 
                a.aim, 
                a.status, 
                a.created, 
                a.updated,
                
                e.bki_data, e.fns_data, e.fetched_at,
                
                sr.final_score, sr.risk_category,
                sr.factors, sr.recommendation
                
            FROM applications a
            JOIN clients cl ON cl.id = a.client_id
            JOIN companies co ON co.id = a.company_id
            
            LEFT JOIN LATERAL (
                SELECT * FROM externaldata 
                WHERE inn = co.inn 
                ORDER BY fetched_at DESC 
                LIMIT 1
            ) e ON TRUE

            LEFT JOIN scoringresults sr ON sr.application_id = a.id
            
            WHERE a.id = %s
            """, (id,))
            row = cur.fetchone()
            return dict(row) if row else None

def get_scoringresults():
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT sr.application_id, sr.final_score, sr.risk_category,
                   sr.factors, sr.recommendation
            FROM scoringresults sr 
            """)
            row = cur.fetchall()
            return row

def get_scoring_results_by_id(id : int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT sr.application_id, sr.final_score, sr.risk_category,
                   sr.factors, sr.recommendation
            FROM scoringresults sr
            WHERE sr.id = %s
            """, (id,))
            row = cur.fetchone()
            if row is None:
                return None
            return row

def get_ailogs():
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.application_id, a.source, a.prompt,
                   a.ai_anwer_text, a.ai_answer_parsed, a.data
            FROM ailogs a
            """)
            row = cur.fetchall()
            return row    

def create_application(client_id:int, company_id:int, application_type:str, amount:int,
                    term_value:int, term_unit:str, aim:str, status:str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            INSERT INTO applications (client_id, company_id, application_type, amount,
                    term_value, term_unit, aim, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
            """, (client_id, company_id, application_type, amount,
                    term_value, term_unit, aim, status))
            return cur.fetchone()


def create_scoringresult(application_id : int, final_score : int, risk_category : str, factors : dict, recommendation:str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            INSERT INTO scoringresults (application_id, final_score, risk_category, factors, recommendation) 
                        VALUES (%s,%s,%s,%s,%s)
                        RETURNING id
            """, (application_id, final_score, risk_category, factors, recommendation))
            return cur.fetchone()

def create_ailog(application_id:int, source:str, prompt: dict, ai_answer_text:str, ai_answer_parsed:dict|None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            INSERT INTO ailogs (application_id, source, prompt, ai_answer_text, ai_answer_parsed) 
                        VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, (application_id, source, prompt, ai_answer_text, ai_answer_parsed))
            return cur.fetchone()
        
def update_application(id:int, status : str | None = None, amount : int | None = None,
                              term_value: int | None = None, term_unit : str | None = None,
                              aim : str | None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            UPDATE applications 
                  SET status = COALESCE(%s, status),
                      amount = COALESCE(%s, amount),
                      term_value = COALESCE(%s, term_value),
                      term_unit = COALESCE(%s, term_unit),
                      aim = COALESCE(%s, aim),
                      updated = now()
            WHERE id = %s
            """, (status,amount, term_value, term_unit, aim,  id))
        
def update_scoringresult(id:int, final_score : int | None = None, risk_category : str | None = None,
                              factors : str | None = None, recommendation : str | None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(""" 
            UPDATE scoringresults
                  SET final_score = COALESCE(%s, final_score),
                  risk_category = COALESCE(%s, risk_category),
                  factors = COALESCE(%s, factors),
                  recommendation = COALESCE(%s, recommendation)
            WHERE id = %s
            """, (final_score, risk_category, factors, recommendation, id))

def delete_application(id:int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(""" 
            DELETE FROM applications
            WHERE id = %s
            """, (id,))
    
def delete_scoringresult(id:int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(""" 
            DELETE FROM scoringresults
            WHERE id = %s
            """, (id,))
        
