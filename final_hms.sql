create database hms;
use hms;
create table admin(E_ID varchar(5) primary key,AName varchar(50),Salary decimal(10,2),Sex varchar(20),State varchar(50),City varchar(50), Pin_no int);

CREATE TABLE admin_mob_no (
    E_ID varchar(5) primary key, 
    Mob_no bigint,
    FOREIGN KEY (E_ID) REFERENCES admin(E_ID)
);

CREATE TABLE bills (
    B_ID INT PRIMARY KEY, 
    Amount DECIMAL(10,2) CHECK (Amount >= 0)  -- Ensuring non-negative amount
);

CREATE TABLE patient (
    P_ID INT PRIMARY KEY, 
    DOB DATE, 
    PName VARCHAR(50), 
    Gender VARCHAR(10) CHECK (Gender IN ('Male', 'Female', 'Others')), 
    Height DECIMAL(5,2), 
    Weight DECIMAL(5,2)
);

CREATE TABLE bills_pays (
    B_ID INT, 
    Amount DECIMAL(10,2), 
    P_ID INT, 
    PRIMARY KEY (B_ID, P_ID), 
    FOREIGN KEY (B_ID) REFERENCES bills(B_ID), 
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID)
);

CREATE TABLE doctor (
    E_ID varchar(5) PRIMARY KEY, 
    DName VARCHAR(50), 
    Salary DECIMAL(10,2) CHECK (Salary >= 0), 
    Sex VARCHAR(10) CHECK (Sex IN ('Male', 'Female', 'Others')), 
    State VARCHAR(50), 
    City VARCHAR(50), 
    Pin_no int 
);

CREATE TABLE consults (
    P_ID INT, 
    E_ID varchar(5), 
    PRIMARY KEY (P_ID, E_ID), 
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID), 
    FOREIGN KEY (E_ID) REFERENCES doctor(E_ID)  -- Assuming consults involve doctors/admin
);

CREATE TABLE doctor_mob_no (
    E_ID varchar(5), 
    Mob_no bigint, 
    Specialisation VARCHAR(50), 
    PRIMARY KEY (E_ID, Mob_no), 
    FOREIGN KEY (E_ID) REFERENCES doctor(E_ID)
);

CREATE TABLE generates (
    E_ID varchar(5), 
    B_ID INT, 
    PRIMARY KEY (E_ID, B_ID), 
    FOREIGN KEY (E_ID) REFERENCES admin(E_ID), 
    FOREIGN KEY (B_ID) REFERENCES bills(B_ID)
);

CREATE TABLE rooms (
    R_ID INT PRIMARY KEY, 
    RType VARCHAR(50), 
    Capacity INT, 
    Availability int check(Availability in (0,1))
);

CREATE TABLE governs (
    E_ID varchar(5), 
    R_ID INT, 
    PRIMARY KEY (E_ID, R_ID), 
    FOREIGN KEY (E_ID) REFERENCES admin(E_ID), 
    FOREIGN KEY (R_ID) REFERENCES rooms(R_ID)
);

CREATE TABLE record (
    Rec_ID INT PRIMARY KEY, 
    P_ID INT, 
    Treatment TEXT, 
    E_ID varchar(5), 
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID), 
    FOREIGN KEY (E_ID) REFERENCES doctor(E_ID) -- Assuming only doctors manage treatments
);

CREATE TABLE maintains (
    E_ID varchar(5), 
    Rec_ID INT, 
    PRIMARY KEY (E_ID, Rec_ID), 
    FOREIGN KEY (E_ID) REFERENCES admin(E_ID), 
    FOREIGN KEY (Rec_ID) REFERENCES record(Rec_ID)
);


CREATE TABLE patient_assigned (
    P_ID INT PRIMARY KEY, 
    DOB DATE, 
    PName VARCHAR(50), 
    Gender VARCHAR(10) CHECK (Gender IN ('Male', 'Female', 'Others')), 
    Height DECIMAL(5,2), 
    Weight DECIMAL(5,2), 
    R_ID INT, 
    FOREIGN KEY (R_ID) REFERENCES rooms(R_ID)
);

CREATE TABLE patient_mob_no (
    P_ID INT, 
    Mob_no bigint, 
    PRIMARY KEY (P_ID, Mob_no), 
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID)
);

CREATE TABLE test_takes (
    Test_type VARCHAR(50), 
    Result text, 
    P_ID INT, 
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID)
);


-- Insert into admin
INSERT INTO admin (E_ID, AName, Salary, Sex, State, City, Pin_no) VALUES
('A1', 'Sneha Iyer', 52000.00, 'Female', 'Karnataka', 'Bangalore', 560001);

-- Insert into admin_mob_no
INSERT INTO admin_mob_no (E_ID, Mob_no) VALUES
('A1', 9876543210);

-- Insert into rooms
INSERT INTO rooms (R_ID, RType, Capacity, Availability) VALUES
(101, 'General', 2, 1),
(102, 'ICU', 1, 1),
(103, 'Private', 1, 1),
(104, 'Semi-Private', 2, 1),
(105, 'Deluxe', 1, 1);

-- Insert into governs
INSERT INTO governs (E_ID, R_ID) VALUES
('A1', 101),
('A1', 102),
('A1', 103),
('A1', 104),
('A1', 105);

CREATE TABLE patient_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL
);

CREATE TABLE emp_users (
    id varchar(5) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL
);

CREATE TABLE appointments (
    pid int not null,
    did varchar(5) not null,
    dates date NOT NULL,
    times time not null,
    cur_status int
);


insert into emp_users values('A1','sneha','4aeb7ad6d5d37a041c4c5ce6562bf9e3caf05a42d931cef4d9e2a60ca623194d');
INSERT INTO doctor values('D1', 'Smith', 52000.00, 'male', 'Karnataka', 'Bangalore', 560001);
insert into doctor_mob_no values('D1',9876543211,'heart');
update doctor set DName='Dr. Smith' where E_ID='D1';
insert into emp_users values('D1','Dr. Smith','4aeb7ad6d5d37a041c4c5ce6562bf9e3caf05a42d931cef4d9e2a60ca623194d');
INSERT INTO doctor values('D2', 'Dr. Johnson', 52000.00, 'male', 'Karnataka', 'Bangalore', 560001);
INSERT INTO doctor values('D3', 'Dr. Lee', 52000.00, 'male', 'Karnataka', 'Bangalore', 560001);
insert into emp_users values('D2','Dr. Johnson','4aeb7ad6d5d37a041c4c5ce6562bf9e3caf05a42d931cef4d9e2a60ca623194d');
insert into emp_users values('D3','Dr. Lee','4aeb7ad6d5d37a041c4c5ce6562bf9e3caf05a42d931cef4d9e2a60ca623194d');
ALTER TABLE generates ADD COLUMN date_generated DATETIME DEFAULT CURRENT_TIMESTAMP;
