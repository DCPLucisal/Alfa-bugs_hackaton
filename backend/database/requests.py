import backend.database.db as db
import bcrypt
from psycopg2.extras import RealDictCursor, Json

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
        
def get_companies_by_client_id(id:int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT c.id, co.inn 
            FROM clients c
            JOIN companies co on co.client_id = c.id
            WHERE c.id = %s
            """, (id,))
            row = cur.fetchall()
            return row if row else []

def get_company_data(inn: str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                c.id AS company_id, 
                e.bki_data, 
                e.fns_data, 
                e.fetched_at
            FROM externaldata e
            LEFT JOIN companies c ON c.inn = e.inn
            WHERE e.inn = %s
            ORDER BY e.fetched_at DESC
            LIMIT 1
            """, (inn,))
            row = cur.fetchone()    
            if row is None:
                return None
            return row
        
def get_company_data_by_application_id(application_id: int) -> dict | None:
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                co.inn,
                e.fns_data,
                e.bki_data
            FROM applications a
            JOIN companies co ON co.id = a.company_id
            LEFT JOIN LATERAL (
                SELECT fns_data, bki_data FROM externaldata 
                WHERE inn = co.inn 
                ORDER BY fetched_at DESC 
                LIMIT 1
            ) e ON TRUE
            WHERE a.id = %s
            """, (application_id,))
            row = cur.fetchone()
            return dict(row) if row else None

def get_applications_for_analysis():
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.id AS application_id,cl.name, cl.lastname, cl.middlename, cl.phone_number,cl.email,
                   co.inn, a.type,a.amount, a.term_value, 
                   a.term_unit, a.aim, a.status, a.created, a.updated,
                   sr.risk_category
            FROM applications a
            JOIN clients cl on cl.id = a.client_id
            JOIN companies co on co.id = a.company_id
            JOIN scoringresults sr on sr.application_id = a.id
            WHERE a.status IN ('validating', 'scoring')
            """)
            row = cur.fetchall()
            return row
        
def get_users_applications(client_id: int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.id,cl.name, cl.lastname, cl.middlename, cl.phone_number,cl.email,
                   co.inn, a.type,a.amount, a.term_value, 
                   a.term_unit, a.aim, a.status, a.created, a.updated,
                   a.manager_comment,sr.risk_category
            FROM applications a
            JOIN clients cl on cl.id = a.client_id
            JOIN companies co on co.id = a.company_id
            LEFT JOIN scoringresults sr on sr.application_id = a.id
            WHERE a.client_id = %s
            """, (client_id,))
            row = cur.fetchall()
            return row
        
def get_scoring_data_by_application_id(application_id: int) -> dict | None:
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                e.fns_data,
                e.bki_data,
                a.amount,
                a.term_value,
                a.term_unit
            FROM applications a
            JOIN companies co ON co.id = a.company_id
            LEFT JOIN LATERAL (
                SELECT fns_data, bki_data FROM externaldata 
                WHERE inn = co.inn 
                ORDER BY fetched_at DESC 
                LIMIT 1
            ) e ON TRUE
            WHERE a.id = %s
            """, (application_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        
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
                a.type, 
                a.amount, 
                a.term_value, 
                a.term_unit, 
                a.aim, 
                a.status, 
                a.created, 
                a.updated,
                a.manager_comment,
                
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

def get_scoring_result_by_application_id(application_id : int):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT sr.application_id, sr.final_score, sr.risk_category,
                   sr.factors, sr.recommendation
            FROM scoringresults sr
            WHERE sr.application_id = %s
            """, (application_id,))
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

def get_ailog_by_application_id(application_id: int, source : str = "user"):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT a.application_id, a.source, a.prompt,
                   a.ai_anwer_text, a.ai_answer_parsed, a.data
            FROM ailogs a
            WHERE a.application_id = %s
                  AND a.source = %s
            ORDER BY a.data DESC LIMIT 1
            """, (application_id, source))
            row = cur.fetchone()
            return row   

def create_application(client_id:int, company_id:int, application_type:str, amount:int,
                    term_value:int, term_unit:str, aim:str, status:str):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            INSERT INTO applications (client_id, company_id, type, amount,
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
            """, (application_id, final_score, risk_category, Json(factors), recommendation))
            return cur.fetchone()

def create_ailog(application_id:int, source:str, prompt: dict, ai_answer_text:str, ai_answer_parsed:dict|None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            INSERT INTO ailogs (application_id, source, prompt, ai_answer_text, ai_answer_parsed) 
                        VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, (application_id, source, Json(prompt), ai_answer_text, Json(ai_answer_parsed) if ai_answer_parsed else None))
            return cur.fetchone()
        
def update_application(id:int, status : str | None = None, amount : int | None = None,
                              term_value: int | None = None, term_unit : str | None = None,
                              aim : str | None = None, manager_comment : str | None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            UPDATE applications 
                  SET status = COALESCE(%s, status),
                      amount = COALESCE(%s, amount),
                      term_value = COALESCE(%s, term_value),
                      term_unit = COALESCE(%s, term_unit),
                      aim = COALESCE(%s, aim),
                      manager_comment = COALESCE(%s,manager_comment),
                      updated = now()
            WHERE id = %s
            """, (status,amount, term_value, term_unit, aim,manager_comment,id))
        
def update_scoringresult_by_application_id(application_id: int, final_score: int | None = None, 
                                            risk_category: str | None = None,
                                            factors: dict | None = None, 
                                            recommendation: str | None = None):
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT id FROM scoringresults 
            WHERE application_id = %s 
            ORDER BY id DESC LIMIT 1
            """, (application_id,))
            sr = cur.fetchone()
            if sr is None:
                return None
            
            cur.execute("""
            UPDATE scoringresults
            SET final_score = COALESCE(%s, final_score),
                risk_category = COALESCE(%s, risk_category),
                factors = COALESCE(%s, factors),
                recommendation = COALESCE(%s, recommendation)
            WHERE id = %s
            RETURNING id
            """, (
                final_score,
                risk_category,
                Json(factors) if factors else None,
                recommendation,
                sr["id"],
            ))
            return cur.fetchone()

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
        
