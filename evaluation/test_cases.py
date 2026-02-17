TEST_CASES = [

    # ---------- BASIC SELECT ----------
    {
        "question": "show all students",
        "gold_sql": "SELECT * FROM STUDENT"
    },
    {
        "question": "show STU_FNAME from STUDENT",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT"
    },
    {
        "question": "show STU_FNAME and STU_LNAME from STUDENT",
        "gold_sql": "SELECT STU_FNAME, STU_LNAME FROM STUDENT"
    },

    # ---------- WHERE CONDITIONS ----------
    {
        "question": "show STU_FNAME from STUDENT where STU_GPA > 3",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_GPA > 3"
    },
    {
        "question": "show STU_FNAME from STUDENT where STU_GPA < 3",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_GPA < 3"
    },
    {
        "question": "show STU_FNAME from STUDENT where STU_CLASS = FR",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_CLASS = 'FR'"
    },

    # ---------- COUNT / AGGREGATION ----------
    {
        "question": "count STUDENT",
        "gold_sql": "SELECT COUNT(*) FROM STUDENT"
    },
    {
        "question": "count DEPARTMENT",
        "gold_sql": "SELECT COUNT(*) FROM DEPARTMENT"
    },
    {
        "question": "count STUDENT where STU_GPA > 3",
        "gold_sql": "SELECT COUNT(*) FROM STUDENT WHERE STU_GPA > 3"
    },

    # ---------- TWO TABLE JOIN ----------
    {
        "question": "show STU_FNAME and DEPT_NAME",
        "gold_sql": "SELECT DEPARTMENT.DEPT_NAME, STUDENT.STU_FNAME FROM DEPARTMENT JOIN STUDENT ON STUDENT.DEPT_CODE = DEPARTMENT.DEPT_CODE"
    },
    {
        "question": "show STU_FNAME from STUDENT and DEPT_NAME from DEPARTMENT where DEPT_CODE = CIS",
        "gold_sql": "SELECT DEPARTMENT.DEPT_NAME, STUDENT.STU_FNAME FROM DEPARTMENT JOIN STUDENT ON STUDENT.DEPT_CODE = DEPARTMENT.DEPT_CODE WHERE DEPARTMENT.DEPT_CODE = 'CIS'"
    },
    {
        "question": "show STU_FNAME from STUDENT and DEPT_NAME from DEPARTMENT where DEPT_NAME = Accounting",
        "gold_sql": "SELECT DEPARTMENT.DEPT_NAME, STUDENT.STU_FNAME FROM DEPARTMENT JOIN STUDENT ON STUDENT.DEPT_CODE = DEPARTMENT.DEPT_CODE WHERE DEPARTMENT.DEPT_NAME = 'Accounting'"
    },

    # ---------- AUTO-CORRECTION TESTS ----------
    {
        "question": "show STU_FNAME from STUDENT and DEPT_NAME from DEPARTMENT where DEPT_NAME = CIS",
        "gold_sql": "SELECT DEPARTMENT.DEPT_NAME, STUDENT.STU_FNAME FROM DEPARTMENT JOIN STUDENT ON STUDENT.DEPT_CODE = DEPARTMENT.DEPT_CODE WHERE DEPARTMENT.DEPT_CODE = 'CIS'"
    },
    {
        "question": "show students from CIS department",
        "gold_sql": "SELECT STUDENT.STU_FNAME FROM STUDENT WHERE DEPT_CODE = 'CIS'"
    },

    # ---------- MORE FILTERS ----------
    {
        "question": "show STU_FNAME where STU_TRANSFER = 1",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_TRANSFER = 1"
    },
    {
        "question": "show STU_FNAME where STU_TRANSFER = 0",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_TRANSFER = 0"
    },

    # ---------- PROFESSOR / EMPLOYEE ----------
    {
        "question": "show all professors",
        "gold_sql": "SELECT * FROM PROFESSOR"
    },
    {
        "question": "count PROFESSOR",
        "gold_sql": "SELECT COUNT(*) FROM PROFESSOR"
    },

    # ---------- COURSE ----------
    {
        "question": "show all courses",
        "gold_sql": "SELECT * FROM COURSE"
    },
    {
        "question": "count COURSE",
        "gold_sql": "SELECT COUNT(*) FROM COURSE"
    },

    # ---------- ENROLL ----------
    {
        "question": "show all enrollments",
        "gold_sql": "SELECT * FROM ENROLL"
    },
    {
        "question": "count ENROLL",
        "gold_sql": "SELECT COUNT(*) FROM ENROLL"
    },

    # ---------- ADVANCED FILTER ----------
    {
        "question": "show STU_FNAME where STU_HRS > 30",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_HRS > 30"
    },
    {
        "question": "show STU_FNAME where STU_GPA > 3 and STU_HRS > 30",
        "gold_sql": "SELECT STU_FNAME FROM STUDENT WHERE STU_GPA > 3 AND STU_HRS > 30"
    },

    # ---------- DEPARTMENT ----------
    {
        "question": "show all departments",
        "gold_sql": "SELECT * FROM DEPARTMENT"
    },
    {
        "question": "count DEPARTMENT where SCHOOL_CODE = BUS",
        "gold_sql": "SELECT COUNT(*) FROM DEPARTMENT WHERE SCHOOL_CODE = 'BUS'"
    },
]