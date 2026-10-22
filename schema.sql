

create type form_type as enum('IP', 'OOO');

create type company_status as enum('active',
	    'process_of_liquidation', 
	    'process_of_reorganization',
		'Bankruptcy',
		'Removed_from_EGRUL');

create type application_type as enum('revolving_credit', 'overdraft');

create type term_unit_type as enum('days', 'months', 'years');

create type application_status as enum('draft',
			'validating',
			'scoring',
			'approved',
			'approved_with_conditions',
			'info_requests',
			'rejected_with_alternative',
			'signed',
			'cancelled');

create type risk_category_type as enum('low', 'middle', 'high');

create type recommendation_type as enum('approve',
			'approve_with_conditions',
			'request_info',
			'rejected_with_alternative',
			'reject',
			'manual_review'
			);

create type request_type as enum('user', 'manager');

create table if not exists Clients(
	id serial primary key,
	name varchar(100) not null,
	lastname varchar(100) not null,
	middlename varchar(100),
	phone_number varchar(20) not null,
	email varchar(100) not null,
	password varchar(100) not null 
);

create table if not exists Companies(
	id serial primary key,
	inn varchar(12) not null unique check(inn ~ '\d{10}$' or inn ~ '\d{12}$'),
	name varchar (500) not null,
	okved varchar (10) not null check(okved ~ '\d{2}(\.\d{1,2}){0,2}'),
	form form_type not null default 'IP', 
	address varchar(150) not null,
	registration_date date not null check (registration_date <= current_date),
	status company_status not null default 'active'
);

create table if not exists Applications(
	id serial primary key,
	client_id int not null references Clients(id),
	company_id int not null references Companies(id),
	type application_type not null default 'revolving_credit',
	amount int not null check (amount > 0),
	term_value int not null check (term_value > 0),
	term_unit term_unit_type not null default 'days',
	aim varchar (300) not null,
	status application_status not null default 'draft',
	created timestamp not null,
	updated timestamp default now()
);

create table if not exists ScoringResults(
	id serial primary key,
	application_id int not null references Applications(id),
	final_score int not null check (final_score >=0 and final_score <= 100),
	risk_category risk_category_type not null,
	factors JSONB not null,
	recommendation recommendation_type not null 
);

create table if not exists ExternalData(
	id serial primary key,
	company_id int not null references Companies(id),
	bki_data JSONB,
	fns_data JSONB,
	fetched_at timestamp
);

create table if not exists AILogs(
	id serial primary key,
	application_id int references Applications(id),
	source request_type not null default 'user',
	prompt JSONB not null,
	ai_answer_text text not null,
	ai_anser_parsed JSONB,
	data timestamp
);

create index if not exists idx_applications_client on Applications(client_id);
create index if not exists idx_applications_company on Applications(company_id);
create index if not exists idx_scoring_application on ScoringResults(application_id);
create index if not exists idx_external_company on ExternalData(company_id);
create index if not exists idx_ailogs_application on AILogs(application_id);

