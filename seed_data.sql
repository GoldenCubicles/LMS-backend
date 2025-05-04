-- Seed script for LMS database with dummy data
-- Adds 3 new institutes, 10 teachers per institute, classes 3-12 with sections A & B, and 10 students per class

-- --------------------------------------------------------
-- 1. Insert sample addresses for institutes
-- --------------------------------------------------------
INSERT INTO core_address (street, city, state, country, postal_code)
VALUES 
    ('123 Central Avenue', 'Metropolis', 'New York', 'USA', '10001'),
    ('456 Ridge Road', 'Hilltown', 'California', 'USA', '90210'),
    ('789 Valley Street', 'Riverdale', 'Texas', 'USA', '75001');

-- --------------------------------------------------------
-- 2. Insert new institutes
-- --------------------------------------------------------
INSERT INTO core_institute (name, address_id)
VALUES 
    ('Excellence Academy', (SELECT id FROM core_address WHERE street = '123 Central Avenue' LIMIT 1)),
    ('Pinnacle Institute', (SELECT id FROM core_address WHERE street = '456 Ridge Road' LIMIT 1)),
    ('Horizon School', (SELECT id FROM core_address WHERE street = '789 Valley Street' LIMIT 1));

-- --------------------------------------------------------
-- 3. Insert addresses for teachers (30 total - 10 per institute)
-- --------------------------------------------------------
INSERT INTO core_address (street, city, state, country, postal_code)
VALUES 
    -- Excellence Academy Teachers (10)
    ('101 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('102 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('103 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('104 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('105 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('106 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('107 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('108 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('109 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    ('110 Teacher Lane', 'Metropolis', 'New York', 'USA', '10001'),
    
    -- Pinnacle Institute Teachers (10)
    ('201 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('202 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('203 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('204 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('205 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('206 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('207 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('208 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('209 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    ('210 Teacher Lane', 'Hilltown', 'California', 'USA', '90210'),
    
    -- Horizon School Teachers (10)
    ('301 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('302 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('303 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('304 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('305 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('306 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('307 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('308 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('309 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001'),
    ('310 Teacher Lane', 'Riverdale', 'Texas', 'USA', '75001');

-- --------------------------------------------------------
-- 4. Insert teachers (10 per institute, 30 total)
-- --------------------------------------------------------
-- Excellence Academy Teachers
INSERT INTO core_teacher (name, email, password, teacher_code, institute_id, address_id)
SELECT 
    CONCAT('Teacher ', (ROW_NUMBER() OVER (ORDER BY a.id)) + 100), 
    CONCAT('teacher', (ROW_NUMBER() OVER (ORDER BY a.id)) + 100, '@excellence.edu'),
    'password123',
    CONCAT('EXC', LPAD((ROW_NUMBER() OVER (ORDER BY a.id)), 3, '0')),
    (SELECT id FROM core_institute WHERE name = 'Excellence Academy'),
    a.id
FROM 
    core_address a
WHERE 
    a.street LIKE '1%Teacher Lane'
LIMIT 10;

-- Pinnacle Institute Teachers
INSERT INTO core_teacher (name, email, password, teacher_code, institute_id, address_id)
SELECT 
    CONCAT('Teacher ', (ROW_NUMBER() OVER (ORDER BY a.id)) + 200), 
    CONCAT('teacher', (ROW_NUMBER() OVER (ORDER BY a.id)) + 200, '@pinnacle.edu'),
    'password123',
    CONCAT('PIN', LPAD((ROW_NUMBER() OVER (ORDER BY a.id)), 3, '0')),
    (SELECT id FROM core_institute WHERE name = 'Pinnacle Institute'),
    a.id
FROM 
    core_address a
WHERE 
    a.street LIKE '2%Teacher Lane'
LIMIT 10;

-- Horizon School Teachers
INSERT INTO core_teacher (name, email, password, teacher_code, institute_id, address_id)
SELECT 
    CONCAT('Teacher ', (ROW_NUMBER() OVER (ORDER BY a.id)) + 300), 
    CONCAT('teacher', (ROW_NUMBER() OVER (ORDER BY a.id)) + 300, '@horizon.edu'),
    'password123',
    CONCAT('HOR', LPAD((ROW_NUMBER() OVER (ORDER BY a.id)), 3, '0')),
    (SELECT id FROM core_institute WHERE name = 'Horizon School'),
    a.id
FROM 
    core_address a
WHERE 
    a.street LIKE '3%Teacher Lane'
LIMIT 10;

-- --------------------------------------------------------
-- 5. Create classrooms (classes 3-12, sections A & B) for each institute
-- --------------------------------------------------------
-- Excellence Academy Classrooms
INSERT INTO core_classroom (class_name, section, class_teacher_id, institute_id, academic_year)
SELECT 
    CONCAT('Class ', class_num),
    section,
    (SELECT id FROM core_teacher WHERE teacher_code = CONCAT('EXC', LPAD(MOD(class_num + ASCII(section) - ASCII('A'), 10) + 1, 3, '0')) LIMIT 1),
    (SELECT id FROM core_institute WHERE name = 'Excellence Academy'),
    2024
FROM 
    (SELECT 3 AS class_num UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 
     UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12) classes,
    (SELECT 'A' AS section UNION SELECT 'B') sections;

-- Pinnacle Institute Classrooms
INSERT INTO core_classroom (class_name, section, class_teacher_id, institute_id, academic_year)
SELECT 
    CONCAT('Class ', class_num),
    section,
    (SELECT id FROM core_teacher WHERE teacher_code = CONCAT('PIN', LPAD(MOD(class_num + ASCII(section) - ASCII('A'), 10) + 1, 3, '0')) LIMIT 1),
    (SELECT id FROM core_institute WHERE name = 'Pinnacle Institute'),
    2024
FROM 
    (SELECT 3 AS class_num UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 
     UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12) classes,
    (SELECT 'A' AS section UNION SELECT 'B') sections;

-- Horizon School Classrooms
INSERT INTO core_classroom (class_name, section, class_teacher_id, institute_id, academic_year)
SELECT 
    CONCAT('Class ', class_num),
    section,
    (SELECT id FROM core_teacher WHERE teacher_code = CONCAT('HOR', LPAD(MOD(class_num + ASCII(section) - ASCII('A'), 10) + 1, 3, '0')) LIMIT 1),
    (SELECT id FROM core_institute WHERE name = 'Horizon School'),
    2024
FROM 
    (SELECT 3 AS class_num UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 
     UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12) classes,
    (SELECT 'A' AS section UNION SELECT 'B') sections;

-- --------------------------------------------------------
-- 6. Insert student addresses
-- --------------------------------------------------------
-- For simplicity, we'll create a batch of addresses that will be used for students
INSERT INTO core_address (street, city, state, country, postal_code)
SELECT 
    CONCAT(student_num, ' Student St, ', institute_area),
    CASE 
        WHEN institute_area = 'Metropolis' THEN 'New York'
        WHEN institute_area = 'Hilltown' THEN 'California'
        ELSE 'Texas'
    END,
    CASE 
        WHEN institute_area = 'Metropolis' THEN 'NY'
        WHEN institute_area = 'Hilltown' THEN 'CA'
        ELSE 'TX'
    END,
    'USA',
    CASE 
        WHEN institute_area = 'Metropolis' THEN '10001'
        WHEN institute_area = 'Hilltown' THEN '90210'
        ELSE '75001'
    END
FROM 
    (SELECT 1 AS student_num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
     UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) student_nums,
    (SELECT 'Class 3A' AS class_section UNION SELECT 'Class 3B' UNION SELECT 'Class 4A' UNION SELECT 'Class 4B'
     UNION SELECT 'Class 5A' UNION SELECT 'Class 5B' UNION SELECT 'Class 6A' UNION SELECT 'Class 6B'
     UNION SELECT 'Class 7A' UNION SELECT 'Class 7B' UNION SELECT 'Class 8A' UNION SELECT 'Class 8B'
     UNION SELECT 'Class 9A' UNION SELECT 'Class 9B' UNION SELECT 'Class 10A' UNION SELECT 'Class 10B'
     UNION SELECT 'Class 11A' UNION SELECT 'Class 11B' UNION SELECT 'Class 12A' UNION SELECT 'Class 12B') class_sections,
    (SELECT 'Metropolis' AS institute_area UNION SELECT 'Hilltown' UNION SELECT 'Riverdale') institute_areas;

-- --------------------------------------------------------
-- 7. Insert students (10 per class per institute)
-- --------------------------------------------------------
-- Excellence Academy Students
INSERT INTO core_student (name, password, roll_number, classroom_id, student_category, gender, institute_id, address_id)
SELECT 
    CONCAT('Student ', ROW_NUMBER() OVER (PARTITION BY class_name, section ORDER BY seq)),
    'password123',
    CONCAT('EXC', SUBSTRING(class_name, 7, 2), section, LPAD(seq, 2, '0')),
    c.id,
    ELT(1 + MOD(seq, 3), 'junior_scholars', 'rising_intellects', 'mastermind_elite'),
    ELT(1 + MOD(seq, 2), 'male', 'female'),
    (SELECT id FROM core_institute WHERE name = 'Excellence Academy'),
    (SELECT id FROM core_address WHERE street LIKE CONCAT(seq, ' Student St, Metropolis%') LIMIT 1)
FROM 
    core_classroom c,
    (SELECT 1 AS seq UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
     UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) seqs
WHERE 
    c.institute_id = (SELECT id FROM core_institute WHERE name = 'Excellence Academy');

-- Pinnacle Institute Students
INSERT INTO core_student (name, password, roll_number, classroom_id, student_category, gender, institute_id, address_id)
SELECT 
    CONCAT('Student ', ROW_NUMBER() OVER (PARTITION BY class_name, section ORDER BY seq)),
    'password123',
    CONCAT('PIN', SUBSTRING(class_name, 7, 2), section, LPAD(seq, 2, '0')),
    c.id,
    ELT(1 + MOD(seq, 3), 'junior_scholars', 'rising_intellects', 'mastermind_elite'),
    ELT(1 + MOD(seq, 2), 'male', 'female'),
    (SELECT id FROM core_institute WHERE name = 'Pinnacle Institute'),
    (SELECT id FROM core_address WHERE street LIKE CONCAT(seq, ' Student St, Hilltown%') LIMIT 1)
FROM 
    core_classroom c,
    (SELECT 1 AS seq UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
     UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) seqs
WHERE 
    c.institute_id = (SELECT id FROM core_institute WHERE name = 'Pinnacle Institute');

-- Horizon School Students
INSERT INTO core_student (name, password, roll_number, classroom_id, student_category, gender, institute_id, address_id)
SELECT 
    CONCAT('Student ', ROW_NUMBER() OVER (PARTITION BY class_name, section ORDER BY seq)),
    'password123',
    CONCAT('HOR', SUBSTRING(class_name, 7, 2), section, LPAD(seq, 2, '0')),
    c.id,
    ELT(1 + MOD(seq, 3), 'junior_scholars', 'rising_intellects', 'mastermind_elite'),
    ELT(1 + MOD(seq, 2), 'male', 'female'),
    (SELECT id FROM core_institute WHERE name = 'Horizon School'),
    (SELECT id FROM core_address WHERE street LIKE CONCAT(seq, ' Student St, Riverdale%') LIMIT 1)
FROM 
    core_classroom c,
    (SELECT 1 AS seq UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
     UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) seqs
WHERE 
    c.institute_id = (SELECT id FROM core_institute WHERE name = 'Horizon School');

-- End of seed script 