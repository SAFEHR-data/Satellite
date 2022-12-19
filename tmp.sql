DROP SCHEMA IF EXISTS star CASCADE;
CREATE SCHEMA star AUTHORIZATION postgres;

CREATE TABLE star.mrn (mrn_id serial PRIMARY KEY, mrn text, nhs_number text, research_opt_out boolean, source_system text, stored_from timestamptz);
  INSERT INTO star.mrn (mrn,nhs_number,research_opt_out,source_system,stored_from) VALUES 
  ('660487647','wLnGi',True,'iWgNZ',timestamp '1987-01-18 08:51:07');
CREATE TABLE star.department (department_id serial PRIMARY KEY, hl7_string text, name text, speciality text);
  INSERT INTO star.department (hl7_string,name,speciality) VALUES 
  ('ITZMj','Nicholas Nolan','RvEJg');
CREATE TABLE star.lab_battery (lab_battery_id serial PRIMARY KEY, battery_code text, battery_name text, description text, lab_provider text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_battery (battery_code,battery_name,description,lab_provider,valid_from,stored_from) VALUES 
  ('wBuNO','nJECH','qdZJa','fUzTY',timestamp '2015-06-21 00:54:24',timestamp '2012-07-20 01:35:46');
CREATE TABLE star.hospital_visit (hospital_visit_id serial PRIMARY KEY, mrn_id bigint REFERENCES star.mrn, source_system text, presentation_datetime timestamptz, admission_datetime timestamptz, discharge_datetime timestamptz, patient_class text, arrival_method text, discharge_destination text, discharge_disposition text, encounter text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.hospital_visit (mrn_id,source_system,presentation_datetime,admission_datetime,discharge_datetime,patient_class,arrival_method,discharge_destination,discharge_disposition,encounter,valid_from,stored_from) VALUES 
  (1,'NFvpU',timestamp '1992-02-17 23:57:25',timestamp '2017-11-19 03:07:33',timestamp '1974-04-15 11:35:02','mKopZ','jZICf','fuGFg','tJsTh','JvInZ',timestamp '2011-01-18 06:14:33',timestamp '2007-03-29 11:28:19');
CREATE TABLE star.lab_sample (lab_sample_id serial PRIMARY KEY, mrn_id bigint REFERENCES star.mrn, external_lab_number text, receipt_at_lab_datetime timestamptz, sample_collection_datetime timestamptz, specimen_type text, sample_site text, collection_method text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_sample (mrn_id,external_lab_number,receipt_at_lab_datetime,sample_collection_datetime,specimen_type,sample_site,collection_method,valid_from,stored_from) VALUES 
  (1,'CfMZy',timestamp '1991-07-30 05:48:46',timestamp '2009-03-04 21:12:25','pslml','cNQqE','efRWi',timestamp '1980-03-06 02:14:52',timestamp '1972-08-18 10:35:31');
CREATE TABLE star.room (room_id serial PRIMARY KEY, department_id bigint REFERENCES star.department, hl7_string text, name text);
  INSERT INTO star.room (department_id,hl7_string,name) VALUES 
  (1,'SIRzT','Kelly Young');
CREATE TABLE star.lab_test_definition (lab_test_definition_id serial PRIMARY KEY, lab_provider text, lab_department text, test_lab_code text, test_standard_code text, standardised_vocabulary text, name text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_test_definition (lab_provider,lab_department,test_lab_code,test_standard_code,standardised_vocabulary,name,valid_from,stored_from) VALUES 
  ('nRLAL','rCFQP','SYwfu','NhFLO','vmpbU','Michael Watson',timestamp '1981-08-08 08:20:16',timestamp '1992-08-18 05:32:30');
CREATE TABLE star.lab_order (lab_order_id serial PRIMARY KEY, lab_sample_id bigint REFERENCES star.lab_sample, hospital_visit_id bigint REFERENCES star.hospital_visit, lab_battery_id bigint REFERENCES star.lab_battery, order_datetime timestamptz, request_datetime timestamptz, clinical_information text, internal_lab_number text, source_system text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_order (lab_sample_id,hospital_visit_id,lab_battery_id,order_datetime,request_datetime,clinical_information,internal_lab_number,source_system,valid_from,stored_from) VALUES 
  (1,1,1,timestamp '1979-12-17 18:14:21',timestamp '2017-06-23 16:44:51','ocKOI','MRebh','OmMKh',timestamp '1996-08-15 13:30:18',timestamp '1976-03-25 00:52:40');
CREATE TABLE star.condition_type (condition_type_id serial PRIMARY KEY, data_type text, internal_code text, name text, sub_type text, standardised_code text, standardised_vocabulary text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.condition_type (data_type,internal_code,name,sub_type,standardised_code,standardised_vocabulary,valid_from,stored_from) VALUES 
  ('xhcMb','mlThE','Robert Giles','bIBNg','qeoeP','twBld',timestamp '2004-04-09 22:52:39',timestamp '2001-10-15 14:37:55');
CREATE TABLE star.bed (bed_id serial PRIMARY KEY, room_id bigint REFERENCES star.room, hl7_string text);
  INSERT INTO star.bed (room_id,hl7_string) VALUES 
  (1,'MgSzm');
CREATE TABLE star.form_definition (form_definition_id serial PRIMARY KEY, internal_id bigint, name text, patient_friendly_name text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.form_definition (internal_id,name,patient_friendly_name,valid_from,stored_from) VALUES 
  (4262,'Nicholas Massey','KkSRn',timestamp '2022-03-21 13:06:59',timestamp '1973-12-13 20:44:05');
CREATE TABLE star.lab_result (lab_result_id serial PRIMARY KEY, lab_order_id bigint REFERENCES star.lab_order, lab_test_definition_id bigint REFERENCES star.lab_test_definition, result_last_modified_datetime timestamptz, abnormal_flag text, mime_type text, value_as_text text, value_as_real real, value_as_bytes bytea, result_operator text, range_high real, range_low real, result_status text, units text, comment text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_result (lab_order_id,lab_test_definition_id,result_last_modified_datetime,abnormal_flag,mime_type,value_as_text,value_as_real,value_as_bytes,result_operator,range_high,range_low,result_status,units,comment,valid_from,stored_from) VALUES 
  (1,1,timestamp '1993-04-18 05:23:04','HqhMC','image/gif','ERAKG',9.39,E'tPwyQ','qjJSa',4.68,7.59,'fvVcI','ripWE','wNsRw',timestamp '2010-03-03 10:21:10',timestamp '2013-02-15 21:19:10');
CREATE TABLE star.visit_observation_type (visit_observation_type_id serial PRIMARY KEY, interface_id bigint, source_observation_type text, id_in_application text, name text, display_name text, description text, is_real_time boolean, has_visit_observation boolean, standardised_code text, standardised_vocabulary text, primary_data_type text, creation_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.visit_observation_type (interface_id,source_observation_type,id_in_application,name,display_name,description,is_real_time,has_visit_observation,standardised_code,standardised_vocabulary,primary_data_type,creation_datetime,valid_from,stored_from) VALUES 
  (2168,'TtyVA','PfaMm','Caitlin Walker','CyTRK','AczSK',True,False,'kCeqS','kCHFJ','MWacF',timestamp '1992-03-07 09:06:51',timestamp '1991-03-28 05:59:41',timestamp '2001-10-09 16:04:02');
CREATE TABLE star.question (question_id serial PRIMARY KEY, question text, stored_from timestamptz, valid_from timestamptz);
  INSERT INTO star.question (question,stored_from,valid_from) VALUES 
  ('dZZAm',timestamp '2007-05-01 14:00:59',timestamp '2013-01-30 12:09:06');
CREATE TABLE star.patient_condition (patient_condition_id serial PRIMARY KEY, condition_type_id bigint REFERENCES star.condition_type, internal_id bigint, mrn_id bigint REFERENCES star.mrn, hospital_visit_id bigint REFERENCES star.hospital_visit, added_datetime timestamptz, added_date date, resolution_datetime timestamptz, resolution_date date, onset_date date, classification text, status text, priority text, comment text, severity text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.patient_condition (condition_type_id,internal_id,mrn_id,hospital_visit_id,added_datetime,added_date,resolution_datetime,resolution_date,onset_date,classification,status,priority,comment,severity,valid_from,stored_from) VALUES 
  (1,2138,1,1,timestamp '2016-03-04 13:57:57',timestamp '1998-05-30',timestamp '1991-07-08 15:00:37',timestamp '1970-03-26',timestamp '1984-07-13','aTWaR','HNgmh','MPmtr','SlgEz','OfbrC',timestamp '1977-11-17 17:05:53',timestamp '1987-06-16 01:30:48');
CREATE TABLE star.bed_state (bed_state_id serial PRIMARY KEY, bed_id bigint REFERENCES star.bed, csn bigint, is_in_census boolean, is_bunk boolean, status text, pool_bed_count bigint);
  INSERT INTO star.bed_state (bed_id,csn,is_in_census,is_bunk,status,pool_bed_count) VALUES 
  (1,8533,True,False,'jrbcc',3370);
CREATE TABLE star.location (location_id serial PRIMARY KEY, location_string text, department_id bigint REFERENCES star.department, room_id bigint REFERENCES star.room, bed_id bigint REFERENCES star.bed);
  INSERT INTO star.location (location_string,department_id,room_id,bed_id) VALUES 
  ('RqJux',1,1,1);
CREATE TABLE star.advance_decision_type (advance_decision_type_id serial PRIMARY KEY, name text, care_code text);
  INSERT INTO star.advance_decision_type (name,care_code) VALUES 
  ('Jacqueline Medina','nyLsa');
CREATE TABLE star.form (form_id serial PRIMARY KEY, form_definition_id bigint REFERENCES star.form_definition, mrn_id bigint REFERENCES star.mrn, hospital_visit_id bigint REFERENCES star.hospital_visit, note_id bigint, first_filed_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.form (form_definition_id,mrn_id,hospital_visit_id,note_id,first_filed_datetime,valid_from,stored_from) VALUES 
  (1,1,1,5462,timestamp '1992-12-19 21:11:39',timestamp '1994-12-27 20:12:38',timestamp '2018-11-23 09:36:14');
CREATE TABLE star.form_question (form_question_id serial PRIMARY KEY, internal_id bigint, concept_name text, concept_abbrev_name text, description text, internal_value_type text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.form_question (internal_id,concept_name,concept_abbrev_name,description,internal_value_type,valid_from,stored_from) VALUES 
  (1535,'vXNcc','rkjLs','xzJis','hEUpd',timestamp '1990-12-14 09:26:01',timestamp '1982-03-22 15:43:31');
CREATE TABLE star.consultation_type (consultation_type_id serial PRIMARY KEY, code text, name text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.consultation_type (code,name,valid_from,stored_from) VALUES 
  ('HUetz','Elizabeth Rodriguez',timestamp '2008-03-01 12:06:58',timestamp '2002-09-29 14:27:13');
CREATE TABLE star.lab_isolate (lab_isolate_id serial PRIMARY KEY, lab_result_id bigint REFERENCES star.lab_result, lab_internal_id bigint, isolate_code text, isolate_name text, culture_type text, quantity text, clinical_information text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_isolate (lab_result_id,lab_internal_id,isolate_code,isolate_name,culture_type,quantity,clinical_information,valid_from,stored_from) VALUES 
  (1,5522,'ZZvhE','hSFBc','tvVRj','kOKyZ','OfeZf',timestamp '1983-06-24 07:37:45',timestamp '2021-01-11 02:37:27');
CREATE TABLE star.visit_observation (visit_observation_id serial PRIMARY KEY, visit_observation_type_id bigint REFERENCES star.visit_observation_type, hospital_visit_id bigint REFERENCES star.hospital_visit, observation_datetime timestamptz, value_as_text text, value_as_real real, value_as_date date, unit text, comment text, source_system text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.visit_observation (visit_observation_type_id,hospital_visit_id,observation_datetime,value_as_text,value_as_real,value_as_date,unit,comment,source_system,valid_from,stored_from) VALUES 
  (1,1,timestamp '1996-03-09 13:14:28','agzJH',2.96,timestamp '2000-07-10','FYLTR','nBfxo','qLXkB',timestamp '1983-01-23 19:39:43',timestamp '1994-05-26 01:44:21');
CREATE TABLE star.request_answer (request_answer_id serial PRIMARY KEY, answer text, question_id bigint REFERENCES star.question, parent_table text, parent_id bigint, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.request_answer (answer,question_id,parent_table,parent_id,valid_from,stored_from) VALUES 
  ('heSbH',1,'WRmhF',6520,timestamp '1987-06-15 20:05:04',timestamp '1984-02-07 18:41:10');
CREATE TABLE star.allergen_reaction (allergen_reaction_id serial PRIMARY KEY, patient_condition_id bigint REFERENCES star.patient_condition, name text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.allergen_reaction (patient_condition_id,name,valid_from,stored_from) VALUES 
  (1,'Rebecca Hanson MD',timestamp '2001-03-12 19:02:56',timestamp '1995-09-23 00:51:02');
CREATE TABLE star.condition_visits (condition_visits_id serial PRIMARY KEY, condition_visit_id bigint, hospital_visit_id bigint REFERENCES star.hospital_visit, patient_condition_id bigint REFERENCES star.patient_condition);
  INSERT INTO star.condition_visits (condition_visit_id,hospital_visit_id,patient_condition_id) VALUES 
  (5925,1,1);
CREATE TABLE star.room_state (room_state_id serial PRIMARY KEY, room_id bigint REFERENCES star.room, csn bigint, status text, is_ready boolean);
  INSERT INTO star.room_state (room_id,csn,status,is_ready) VALUES 
  (1,2431,'KzORB',True);
CREATE TABLE star.bed_facility (bed_facility_id serial PRIMARY KEY, bed_state_id bigint REFERENCES star.bed_state, type text);
  INSERT INTO star.bed_facility (bed_state_id,type) VALUES 
  (1,'FFOQm');
CREATE TABLE star.department_state (department_state_id serial PRIMARY KEY, department_id bigint REFERENCES star.department, status text);
  INSERT INTO star.department_state (department_id,status) VALUES 
  (1,'avTVu');
CREATE TABLE star.location_visit (location_visit_id serial PRIMARY KEY, hospital_visit_id bigint REFERENCES star.hospital_visit, parent_location_visit_id bigint, admission_datetime timestamptz, discharge_datetime timestamptz, location_id bigint REFERENCES star.location, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.location_visit (hospital_visit_id,parent_location_visit_id,admission_datetime,discharge_datetime,location_id,valid_from,stored_from) VALUES 
  (1,581,timestamp '2005-09-25 14:45:21',timestamp '1980-02-05 16:17:34',1,timestamp '2011-01-03 08:58:37',timestamp '1980-08-11 01:10:09');
CREATE TABLE star.planned_movement (planned_movement_id serial PRIMARY KEY, hospital_visit_id bigint REFERENCES star.hospital_visit, location_id bigint REFERENCES star.location, event_type text, event_datetime timestamptz, cancelled_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.planned_movement (hospital_visit_id,location_id,event_type,event_datetime,cancelled_datetime,valid_from,stored_from) VALUES 
  (1,1,'TTZEe',timestamp '1975-10-05 19:35:44',timestamp '2005-02-24 08:50:06',timestamp '1972-09-06 16:27:39',timestamp '1974-07-08 06:06:47');
CREATE TABLE star.advance_decision (advance_decision_id serial PRIMARY KEY, advance_decision_type_id bigint REFERENCES star.advance_decision_type, hospital_visit_id bigint REFERENCES star.hospital_visit, internal_id bigint, status_change_datetime timestamptz, requested_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.advance_decision (advance_decision_type_id,hospital_visit_id,internal_id,status_change_datetime,requested_datetime,valid_from,stored_from) VALUES 
  (1,1,665,timestamp '1990-06-12 16:23:20',timestamp '1971-01-15 21:56:17',timestamp '2021-08-23 12:43:23',timestamp '2000-07-11 17:49:04');
CREATE TABLE star.core_demographic (core_demographic_id serial PRIMARY KEY, mrn_id bigint REFERENCES star.mrn, firstname text, middlename text, lastname text, date_of_birth date, date_of_death date, datetime_of_birth timestamptz, datetime_of_death timestamptz, alive boolean, home_postcode text, sex text, ethnicity text, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.core_demographic (mrn_id,firstname,middlename,lastname,date_of_birth,date_of_death,datetime_of_birth,datetime_of_death,alive,home_postcode,sex,ethnicity,valid_from,stored_from) VALUES 
  (1,'kZjPD','xGyHG','cKfRY',timestamp '2016-07-16',timestamp '2005-04-01',timestamp '2021-07-28 08:58:37',timestamp '2010-11-03 14:48:56',False,'VBWns','IMAEY','yMLoZ',timestamp '1971-05-25 01:51:29',timestamp '2014-09-16 10:32:53');
CREATE TABLE star.mrn_to_live (mrn_to_live_id serial PRIMARY KEY, mrn_id bigint REFERENCES star.mrn, live_mrn_id bigint, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.mrn_to_live (mrn_id,live_mrn_id,valid_from,stored_from) VALUES 
  (1,2981,timestamp '1990-08-01 05:42:25',timestamp '2004-06-29 00:26:52');
CREATE TABLE star.form_answer (form_answer_id serial PRIMARY KEY, form_question_id bigint REFERENCES star.form_question, form_id bigint REFERENCES star.form, internal_id bigint, context text, value_as_text text, value_as_number real, value_as_boolean boolean, value_as_datetime timestamptz, value_as_date date, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.form_answer (form_question_id,form_id,internal_id,context,value_as_text,value_as_number,value_as_boolean,value_as_datetime,value_as_date,valid_from,stored_from) VALUES 
  (1,1,1075,'FqtXA','yZydk',6.56,False,timestamp '1986-04-06 04:14:25',timestamp '1989-07-15',timestamp '2019-08-22 14:16:02',timestamp '1992-09-24 05:27:58');
CREATE TABLE star.consultation_request (consultation_request_id serial PRIMARY KEY, consultation_type_id bigint REFERENCES star.consultation_type, hospital_visit_id bigint REFERENCES star.hospital_visit, internal_id bigint, comments text, status_change_datetime timestamptz, scheduled_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.consultation_request (consultation_type_id,hospital_visit_id,internal_id,comments,status_change_datetime,scheduled_datetime,valid_from,stored_from) VALUES 
  (1,1,7886,'AjFMT',timestamp '1975-07-22 16:00:38',timestamp '2015-11-02 00:31:56',timestamp '2017-07-19 04:38:24',timestamp '1980-04-20 09:58:11');
CREATE TABLE star.lab_battery_element (lab_battery_element_id serial PRIMARY KEY, lab_battery_id bigint REFERENCES star.lab_battery, lab_test_definition_id bigint REFERENCES star.lab_test_definition, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_battery_element (lab_battery_id,lab_test_definition_id,valid_from,stored_from) VALUES 
  (1,1,timestamp '1972-05-24 09:33:43',timestamp '2011-08-19 15:32:09');
CREATE TABLE star.lab_sensitivity (lab_sensitivity_id serial PRIMARY KEY, lab_isolate_id bigint REFERENCES star.lab_isolate, agent text, sensitivity text, reporting_datetime timestamptz, valid_from timestamptz, stored_from timestamptz);
  INSERT INTO star.lab_sensitivity (lab_isolate_id,agent,sensitivity,reporting_datetime,valid_from,stored_from) VALUES 
  (1,'yDdgE','XjbcM',timestamp '2012-01-06 13:42:05',timestamp '1979-01-12 07:47:55',timestamp '2012-11-13 21:31:56');
