-- Use this DDL and one of the following command sequences to create an 'org' 
--   database to demonstrate the function of some SLQPASPlugins
-- This version currently provides data suitable for
--   SQL User Manager
--   SQL Role Manager
--   SQL Mutable Property Provider
-- russf@topia.com

-- For sqlite
-- ===========
-- % cd <INSTANCE>/var/sqlite...
-- % cat <path>/structure.sql | sqlite3 org.db

-- For mySql
-- =========
-- assuming :
--   you know the root password 
--   and there is already a database 'org'
--   and the mysql service is on localhost
-- % mysql -u root -p org -h localhost < structure.sql

-- Notes on the schema
-- ===================
-- the password field width allows for up to 40 chars of encryption

--CREATE TABLE users(username varchar(20) primary key, password varchar(45), firstname varchar(20), lastname varchar(20), email varchar(50));
CREATE TABLE users(username varchar(20) primary key, password varchar(45), fullname varchar(30), email varchar(50));
INSERT INTO users VALUES('u1', 'pass', 'Mr. One', 'one@1.com');
INSERT INTO users VALUES('u2', 'pass', 'Herr Zwei', 'two@2.com');
INSERT INTO users VALUES('u3', 'pass', 'Msr. Troi', 'three@3.com');

CREATE TABLE roles(username varchar(20), rolename varchar(20));
INSERT INTO roles VALUES('u1', 'Other');
INSERT INTO roles VALUES('u2', 'Manager');
INSERT INTO roles VALUES('u3', 'Member');
-- a second role for this user
INSERT INTO roles VALUES('u1', 'Manager'); 

