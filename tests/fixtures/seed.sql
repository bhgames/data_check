drop database if exists test cascade;

create database test;

CREATE TABLE test.test_col_comparison_fail (                            
   x INT,                                                                
   y INT                                                                 
 );

insert into test.test_col_comparison_fail(x,y) values (1,1);


 CREATE TABLE test.test_col_comparison_success (                            
   x INT,                                                                   
   y INT                                                                    
 );

insert into test.test_col_comparison_success(x,y) values (1,2);


CREATE TABLE test.test_date_gap_fail (                            
   updated_at TIMESTAMP                                            
 );


insert into test.test_date_gap_fail(updated_at) values
  ('2015-02-02 00:00:00'), 
  ('2015-02-06 00:00:00'), 
  ('2015-02-03 00:00:00'), 
  ('2015-01-01 00:00:00'), 
  ('2015-01-03 00:00:00');

CREATE TABLE test.test_date_gap_fail_string_updated_at (                            
   updated_at STRING                                                                 
 );

insert into test.test_date_gap_fail_string_updated_at(updated_at) values
  ('2015-02-09 00:02:00'), 
  ('2015-02-12 00:02:00'), 
  ('2015-02-13 00:02:00'), 
  ('2015-02-10 00:02:00');

CREATE TABLE test.test_date_gap_success (                            
   updated_at TIMESTAMP                                               
 );


insert into test.test_date_gap_success(updated_at) values
  ('2015-01-02 00:00:00'),
  ('2015-01-04 00:00:00'),
  ('2015-01-03 00:00:00'),
  ('2015-01-02 00:00:00'),
  ('2015-01-01 00:00:00');

CREATE TABLE test.test_date_gap_success_same_day_events (                            
   updated_at TIMESTAMP                                                               
 );

insert into test.test_date_gap_success_same_day_events(updated_at) values
  ('2015-02-06 00:02:00'),
  ('2015-02-07 00:02:00'),
  ('2015-02-06 00:00:00');


CREATE TABLE test.test_date_gap_success_string_updated_at (                            
   updated_at STRING                                                                    
 );

insert into test.test_date_gap_success_string_updated_at(updated_at) values
  ('2015-02-09 00:02:00'),
  ('2015-02-10 00:02:00'),
  ('2015-02-11 00:03:00'),
  ('2015-02-11 00:02:00');


CREATE TABLE test.test_id_gap (                            
   id INT                                                   
 );

insert into test.test_id_gap(id) values
  (1), (5);

CREATE TABLE test.test_null_fail (                            
   id INT,                                                     
   status STRING                                               
 );

insert into test.test_null_fail(id, status) values
  (1, NULL);


CREATE TABLE test.test_null_success (                            
   id INT,                                                        
   status STRING                                                  
 );


insert into test.test_null_success(id, status) values
  (1, 'okay');


 CREATE TABLE test.test_uniqueness_fail (                            
   id INT                                                            
 );


insert into test.test_uniqueness_fail(id) values
  (1), (2), (1);

CREATE TABLE test.test_uniqueness_success (                            
   id INT                                                               
 );

insert into test.test_uniqueness_success(id) values
  (1), (2);


--- PK Single FK Success

CREATE TABLE test.test_fk_primary_table_single_fk_success (                            
   id INT,
   test_fk_secondary_table_single_fk_success_id INT                            
 );

insert into test.test_fk_primary_table_single_fk_success(id, test_fk_secondary_table_single_fk_success_id) values
  (1,1), (2,2), (3, NULL);


CREATE TABLE test.test_fk_secondary_table_single_fk_success (                            
   id INT
 );

insert into test.test_fk_secondary_table_single_fk_success(id) values
  (1), (2);


-- Single FK Fail

CREATE TABLE test.test_fk_primary_table_single_fk_fail (                            
   id INT,
   test_fk_secondary_table_single_fk_fail_id INT                            
 );

insert into test.test_fk_primary_table_single_fk_fail(id, test_fk_secondary_table_single_fk_fail_id) values
  (1,1), (2,3);


CREATE TABLE test.test_fk_secondary_table_single_fk_fail (                            
   id INT
 );

insert into test.test_fk_secondary_table_single_fk_fail(id) values
  (1), (2);


-- Double FK Success

CREATE TABLE test.test_fk_primary_table_double_fk_success (                            
   id INT,
   test_fk_secondary_table_double_fk_success_id INT,
   test_fk_tertiary_table_double_fk_success_id INT                            
 );

insert into test.test_fk_primary_table_double_fk_success(id, test_fk_secondary_table_double_fk_success_id, test_fk_tertiary_table_double_fk_success_id) values
  (1,1,1), (2,2,2);


CREATE TABLE test.test_fk_secondary_table_double_fk_success (                            
   id INT
 );

insert into test.test_fk_secondary_table_double_fk_success(id) values
  (1), (2);


CREATE TABLE test.test_fk_tertiary_table_double_fk_success (                            
   id INT
 );

insert into test.test_fk_tertiary_table_double_fk_success(id) values
  (1), (2);


-- Double FK Fail

CREATE TABLE test.test_fk_primary_table_double_fk_fail (                            
   id INT,
   test_fk_secondary_table_double_fk_fail_id INT,
   test_fk_tertiary_table_double_fk_fail_id INT                            
 );

insert into test.test_fk_primary_table_double_fk_fail(id, test_fk_secondary_table_double_fk_fail_id, test_fk_tertiary_table_double_fk_fail_id) values
  (1,3,1), (2,2,2);


CREATE TABLE test.test_fk_secondary_table_double_fk_fail (                            
   id INT
 );

insert into test.test_fk_secondary_table_double_fk_fail(id) values
  (1), (2);


CREATE TABLE test.test_fk_tertiary_table_double_fk_fail (                            
   id INT
 );

insert into test.test_fk_tertiary_table_double_fk_fail(id) values
  (1), (2);
