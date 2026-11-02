# Lesson 07: Relational Design, Keys and Data Integrity

## Learning outcomes

Explain entities and attributes; identify primary and foreign keys; understand one-to-one, one-to-many and many-to-many relationships; model those relationships with tables; apply constraints; and explain normalisation at an introductory practical level.

## 1. Model the real-world problem first

Suppose a training centre has learners, courses and enrolments. A learner can enrol in multiple courses, and each course can have many learners. If we put learner details and course details in one enormous table, names, course titles and tutor details repeat. Repetition creates update, insertion and deletion anomalies.

Database design begins by identifying the things (entities) the system needs to remember and the relationships between them.

## 2. Tables represent entities

A simple schema may contain:
- `students`: one row per learner.
- `courses`: one row per course.
- `enrolments`: one row per learner-course registration.

An attribute describes an entity. Student name belongs to students; course title belongs to courses; enrolment date belongs to the relationship represented by enrolments.

## 3. Primary keys

A primary key uniquely identifies each row. It must be unique and cannot be NULL. In SQLite, `INTEGER PRIMARY KEY` aliases the rowid for an ordinary rowid table and automatically assigns an integer when omitted.

```sql
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
```

The ID is a stable identifier. Email is constrained to be unique here, but an email address may change, so it is often better as a unique attribute rather than the primary key. A natural key is based on real-world meaning; a surrogate key is an identifier created for database use.

## 4. Foreign keys

A foreign key links a child record to a referenced parent record:

```sql
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_on TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

The foreign key says an enrolment's student_id must refer to a valid student and its course_id must refer to a valid course—provided foreign-key enforcement is enabled. In SQLite, enable it for each connection:

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    connection.execute("PRAGMA foreign_keys = ON;")
```

Set the pragma immediately after opening each connection and before relying on constraints. Do not assume every SQLite connection has enforcement enabled by default.

## 5. Relationship types

**One-to-one:** one person has one profile record, and each profile belongs to one person. This is often represented with a foreign key that is also UNIQUE.

**One-to-many:** one tutor can teach many courses, but each course has one assigned tutor. Put the tutor's key in the course table as a foreign key.

**Many-to-many:** many students can take many courses. Do not store a list of course IDs in one student cell. Use a junction/associative table such as enrolments, with foreign keys to students and courses.

Diagram:

```text
STUDENTS                 ENROLMENTS                 COURSES
student_id  1 ------<   student_id
                       course_id   >------ 1       course_id
                       enrolled_on              course_title
```

The crow's-foot side represents “many”. A student can have many enrolment rows; a course can also have many enrolment rows.

## 6. Constraints protect data

- `NOT NULL`: a value must be supplied.
- `UNIQUE`: duplicate values are rejected (with SQL NULL nuances).
- `PRIMARY KEY`: unique row identifier.
- `FOREIGN KEY`: enforces a reference to another table when enabled.
- `CHECK`: requires a condition to be true.
- `DEFAULT`: supplies a value when one is omitted.

```sql
CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 100),
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
```

A constraint is not a substitute for thoughtful validation in Python, but it protects the database even when another script writes to it.

## 7. Normalisation

Normalisation is a set of principles for organising relational data to reduce avoidable duplication and update anomalies.

- **First normal form (1NF):** columns contain atomic values for the intended model; avoid packing multiple values into one cell.
- **Second normal form (2NF):** in a table with a composite candidate key, non-key attributes depend on the whole key, not just part of it.
- **Third normal form (3NF):** non-key attributes depend on the key, the whole key and nothing but the key; avoid transitive dependencies between non-key attributes.

Example: if a table stores `student_id`, `course_id`, `student_name` and `course_title`, the student name depends on student_id, and course title depends on course_id. In a junction table whose key is the student/course pair, those descriptive fields do not depend on the whole pair. Store them in their entity tables instead.

Normalisation is not “split everything into as many tables as possible”. It is a way to make dependencies and update rules coherent. Analytical systems sometimes use denormalised structures for performance, but that should be a deliberate choice.

## 8. Create the schema from Python

```python
import sqlite3

schema = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_title TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_on TEXT NOT NULL,
    UNIQUE(student_id, course_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id)
);
"""

with sqlite3.connect("data/learning.db") as connection:
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(schema)
```

The composite UNIQUE constraint prevents the same learner being enrolled in the same course twice in this simplified model. A real system may allow re-enrolment over time and would need a different key or an enrolment-attempt model.

## Guided exercises

1. Identify entities for a library system.
2. Draw a one-to-many relationship between departments and employees.
3. Model a many-to-many relationship between authors and books.
4. Explain why a comma-separated list of course IDs in one field is problematic.
5. Add a CHECK constraint to keep a score between 0 and 100.
6. Explain why foreign-key enforcement must be enabled in SQLite connections.

## Independent practice

Design a database for a small online shop with customers, products, orders and order items. Identify primary keys, foreign keys, relationship cardinalities and at least five constraints. Explain what would go wrong if customer names were used as foreign keys.

## Summary

Good relational design starts with entities and relationships. Primary keys identify rows; foreign keys connect tables. Constraints protect validity. Normalisation reduces update anomalies by placing facts in the tables where they belong.

## Next lesson

Now that we have related tables, we can retrieve information across them using JOIN operations.