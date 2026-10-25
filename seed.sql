
INSERT INTO Clients (name, lastname, middlename, phone_number, email, password) VALUES
('Иван', 'Иванов', 'Иванович', '+79991111111', 'ivan@test.com', 'pass1'),
('Петр', 'Петров', 'Петрович', '+79992222222', 'petr@test.com', 'pass2'),
('Анна', 'Смирнова', 'Сергеевна', '+79993333333', 'anna@test.com', 'pass3');


INSERT INTO Companies (inn, client_id) VALUES
('7701234567', 1),
('500198765432', 2),
('7809876543', 3);


INSERT INTO ExternalData (inn, fns_data, bki_data) VALUES
('7701234567', 
 '{"name": "ООО Ромашка", "kpp": "770101001", "okved": "46.90", "form": "OOO", "status": "active", "registration_date": "2019-03-12"}'::jsonb, 
 '{"found_in_bki": true, "overdue_count_12m": 0}'::jsonb),

('500198765432', 
 '{"name": "ИП Иванов В.В.", "kpp": null, "okved": "47.11", "form": "IP", "status": "active", "registration_date": "2020-06-15"}'::jsonb, 
 '{"found_in_bki": true, "overdue_count_12m": 3}'::jsonb),

('7809876543', 
 '{"name": "ООО ТехноПром", "kpp": "780101001", "okved": "25.11", "form": "OOO", "status": "active", "registration_date": "2015-11-20"}'::jsonb, 
 '{"found_in_bki": true, "overdue_count_12m": 0}'::jsonb);