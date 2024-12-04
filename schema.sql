-- Create schema
CREATE SCHEMA SchoolDB;

-- Use the database
USE SchoolDB;

-- Create the tables

CREATE TABLE Students (
    Student_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(100),
    Last_Name VARCHAR(100),
    Gender VARCHAR(10),
    GPA DECIMAL(3, 2),
    Year INT,
    Email VARCHAR(100),
    Date_of_Birth DATE,
    Major VARCHAR(100),
    Phone_Number VARCHAR(20)
);

CREATE TABLE Buildings (
    Building_ID INT AUTO_INCREMENT PRIMARY KEY,
    Building_Name VARCHAR(100),
    Number_of_Rooms INT,
    CONSTRAINT chk_room_capacity CHECK (Number_of_Rooms < 500)
);

CREATE TABLE Departments (
    Department_ID INT AUTO_INCREMENT PRIMARY KEY,
    Department_Name VARCHAR(100),
    Department_Head_ID INT,  -- Renamed from Professor_ID to Department_Head_ID, allowing NULL values
    Building_ID INT,
    CONSTRAINT fk_department_head FOREIGN KEY (Department_Head_ID) REFERENCES Professors(Professor_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_department_building FOREIGN KEY (Building_ID) REFERENCES Buildings(Building_ID)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Professors (
    Professor_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(100),
    Last_Name VARCHAR(100),
    Email VARCHAR(100),
    Phone_Number VARCHAR(20)
);

CREATE TABLE Classes (
    Class_ID INT AUTO_INCREMENT PRIMARY KEY,
    Class_Name VARCHAR(100),
    Class_Code VARCHAR(20),
    Units INT,
    Time TIME,
    Day VARCHAR(20),
    Semester VARCHAR(20),
    Room VARCHAR(50),
    Building_ID INT,
    Professor_ID INT,
    CONSTRAINT fk_building FOREIGN KEY (Building_ID) REFERENCES Buildings(Building_ID),
    CONSTRAINT fk_professor FOREIGN KEY (Professor_ID) REFERENCES Professors(Professor_ID),
    CONSTRAINT unique_room_time_day UNIQUE (Room, Time, Day)
);
 

-- Create triggers

DELIMITER $$


-- Trigger to check room capacity when adding a new class
CREATE TRIGGER check_room_capacity
BEFORE INSERT ON Classes
FOR EACH ROW
BEGIN
    DECLARE room_capacity INT;
    SELECT Number_of_Rooms INTO room_capacity
    FROM Buildings
    WHERE Building_ID = NEW.Building_ID;
    
    IF NEW.Room > room_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Class exceeds room capacity';
    END IF;
END $$

-- Trigger to ensure professors don’t have overlapping classes
ALTER TABLE Classes
ADD CONSTRAINT unique_professor_class_time_day UNIQUE (Professor_ID, Time, Day);

DELIMITER ;

SELECT DATABASE();
SHOW TABLES;

-- Insert random data into the Professors table
INSERT INTO Professors (First_Name, Last_Name, Email, Phone_Number)
VALUES 
('Alan', 'Turing', 'alan.turing@csun.edu', '818-555-3141'),
('Nikola', 'Tesla', 'nikola.tesla@csun.edu', '818-555-4152'),
('Euclid', 'Mathews', 'euclid.mathews@csun.edu', '818-555-5213'),
('Marie', 'Curie', 'marie.curie@csun.edu', '818-555-6234'),
('Charles', 'Darwin', 'charles.darwin@csun.edu', '818-555-7354');

INSERT INTO Buildings (Building_Name, Number_of_Rooms)
VALUES 
('Science Hall', 120),
('Engineering Building', 200),
('Arts Center', 80),
('Library', 50),
('Computer Lab', 40);

INSERT INTO Departments (Department_Name, Professor_ID, Building_ID)
VALUES 
('Computer Science', 1, 1), 
('Business', 2, 2), 
('Mathematics', 3, 3),
('Physics', 4, 4), 
('Biology', 5, 5); 


