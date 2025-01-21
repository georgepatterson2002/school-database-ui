# school-database-ui

This repository contains the SQL schema and associated scripts for the `SchoolDB` database which can be used to inspect tables and run custom queries. The schema is designed to manage information for a school database, including students, professors, classes, departments, and buildings. It also includes triggers to enforce data integrity and constraints.

## Features

- **Dynamic Relationships**:
  - Students enroll in classes.
  - Professors are assigned to classes.
  - Departments are located in buildings and have department heads.
- **Data Integrity**:
  - Room capacity and scheduling conflicts are managed with constraints and triggers.
  - Referential integrity through foreign keys.
- **Preloaded Data**:
  - Sample data for professors, buildings, and departments.

## Schema Details

### Tables

#### `Students`
| Column         | Type         | Constraints                     |
|----------------|--------------|---------------------------------|
| `Student_ID`   | INT          | Primary Key, Auto Increment     |
| `First_Name`   | VARCHAR(100) |                                 |
| `Last_Name`    | VARCHAR(100) |                                 |
| `Gender`       | VARCHAR(10)  |                                 |
| `GPA`          | DECIMAL(3,2) |                                 |
| `Year`         | INT          |                                 |
| `Email`        | VARCHAR(100) |                                 |
| `Date_of_Birth`| DATE         |                                 |
| `Major`        | VARCHAR(100) |                                 |
| `Phone_Number` | VARCHAR(20)  |                                 |

#### `Buildings`
| Column            | Type         | Constraints                     |
|-------------------|--------------|---------------------------------|
| `Building_ID`     | INT          | Primary Key, Auto Increment     |
| `Building_Name`   | VARCHAR(100) |                                 |
| `Number_of_Rooms` | INT          | `CHECK(Number_of_Rooms < 500)`  |

#### `Departments`
| Column             | Type         | Constraints                                                   |
|--------------------|--------------|---------------------------------------------------------------|
| `Department_ID`    | INT          | Primary Key, Auto Increment                                   |
| `Department_Name`  | VARCHAR(100) |                                                               |
| `Department_Head_ID` | INT        | Foreign Key -> `Professors(Professor_ID)`                    |
| `Building_ID`      | INT          | Foreign Key -> `Buildings(Building_ID)`                      |

#### `Professors`
| Column         | Type         | Constraints                     |
|----------------|--------------|---------------------------------|
| `Professor_ID` | INT          | Primary Key, Auto Increment     |
| `First_Name`   | VARCHAR(100) |                                 |
| `Last_Name`    | VARCHAR(100) |                                 |
| `Email`        | VARCHAR(100) |                                 |
| `Phone_Number` | VARCHAR(20)  |                                 |

#### `Classes`
| Column         | Type         | Constraints                                                   |
|----------------|--------------|---------------------------------------------------------------|
| `Class_ID`     | INT          | Primary Key, Auto Increment                                   |
| `Class_Name`   | VARCHAR(100) |                                                               |
| `Class_Code`   | VARCHAR(20)  |                                                               |
| `Units`        | INT          |                                                               |
| `Time`         | TIME         |                                                               |
| `Day`          | VARCHAR(20)  |                                                               |
| `Semester`     | VARCHAR(20)  |                                                               |
| `Room`         | VARCHAR(50)  | Unique with `Time` and `Day`                                  |
| `Building_ID`  | INT          | Foreign Key -> `Buildings(Building_ID)`                      |
| `Professor_ID` | INT          | Foreign Key -> `Professors(Professor_ID)`                    |

### Triggers

#### Room Capacity Check
Ensures that no class exceeds the maximum capacity of the assigned building.

```sql
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
END;
```

#### Professor Scheduling Conflict
Ensures professors do not have overlapping classes.

```sql
ALTER TABLE Classes
ADD CONSTRAINT unique_professor_class_time_day UNIQUE (Professor_ID, Time, Day);
```

