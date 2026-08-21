#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "student.h"


/* ================================
   DATABASE CONNECTION
   ================================ */

PGconn *connect_db(void) {

    /*
     * Change these values according to
     * your PostgreSQL configuration.
     */
    const char *conninfo =
        "host=localhost "
        "port=5432 "
        "dbname=student_portal "
        "user=postgres "
        "password=postgres ";

    PGconn *conn = PQconnectdb(conninfo);

    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr,
                "Database connection failed: %s\n",
                PQerrorMessage(conn));

        PQfinish(conn);
        return NULL;
    }

    printf("Database connected successfully.\n");

    return conn;
}


void close_db(PGconn *conn) {

    if (conn != NULL) {
        PQfinish(conn);
    }
}


/* ================================
   REGISTER STUDENT
   ================================ */

void register_student(PGconn *conn) {

    char id[10];
    char email[MAX_EMAIL];
    char name[MAX_USERNAME];
    char password[MAX_PASSWORD];

    printf("\n===== STUDENT REGISTRATION =====\n");

    printf("Enter id: ");
    scanf(" %[^\n]", id);

    printf("Enter username: ");
    scanf("%s", name);

    printf("Enter email: ");
    scanf("%s", email);

    printf("Enter password: ");
    scanf("%s", password);


    /*
     * Parameterized query.
     *
     * This is the SECURE version.
     */
    const char *query =
        "INSERT INTO students "
        "(id, name, email, password) "
        "VALUES ($1, $2, $3, $4) "
        "RETURNING id";


    const char *values[4] = {
        id,
        name,
        email,
        password
    };


    PGresult *result =
        PQexecParams(
            conn,
            query,
            4,
            NULL,
            values,
            NULL,
            NULL,
            0
        );


    if (PQresultStatus(result) != PGRES_TUPLES_OK) {

        fprintf(stderr,
                "Registration failed: %s\n",
                PQerrorMessage(conn));

        PQclear(result);
        return;
    }


    charp[10] id = atoi(PQgetvalue(result, 0, 0));

    printf("\nRegistration successful!\n");
    printf("Your Student ID is: %d\n", id);

    PQclear(result);
}


/* ================================
   LOGIN
   ================================ */

int login_student(PGconn *conn,
                  Student *logged_in_student) {

    char name[MAX_USERNAME];
    char password[MAX_PASSWORD];

    printf("\n===== LOGIN =====\n");

    printf("Username: ");
    scanf("%s", name);

    printf("Password: ");
    scanf("%s", password);


    /*
     * Secure parameterized query.
     */
    const char *query =
        "SELECT id, name, email, password "
        "FROM students "
        "WHERE name = $1 AND password = $2";


    const char *values[2] = {
        name,
        password
    };


    PGresult *result =
        PQexecParams(
            conn,
            query,
            2,
            NULL,
            values,
            NULL,
            NULL,
            0
        );


    if (PQresultStatus(result) != PGRES_TUPLES_OK) {

        fprintf(stderr,
                "Login query failed: %s\n",
                PQerrorMessage(conn));

        PQclear(result);
        return 0;
    }


    if (PQntuples(result) == 0) {

        printf("\nInvalid username or password.\n");

        PQclear(result);
        return 0;
    }


    logged_in_student->id =
        atoi(PQgetvalue(result, 0, 0));

    strcpy(
        logged_in_student->name,
        PQgetvalue(result, 0, 1)
    );

    strcpy(
        logged_in_student->email,
        PQgetvalue(result, 0, 2)
    );



    printf("\nLogin successful!\n");
    printf("Welcome, %s!\n",
           logged_in_student->name);


    PQclear(result);

    return 1;
}


/* ================================
   VIEW PROFILE
   ================================ */

void view_profile(PGconn *conn,
                  Student student) {

    (void)conn;

    printf("\n===== STUDENT PROFILE =====\n");

    printf("Student ID : %d\n",
           student.id);

    printf("Name       : %s\n",
           student.name);

    printf("Email      : %s\n",
           student.email);

}


/* ================================
   UPDATE PROFILE
   ================================ */

void update_profile(PGconn *conn,
                    Student *student) {

    char name[MAX_NAME];
    char email[MAX_EMAIL];

    printf("\n===== UPDATE PROFILE =====\n");

    printf("Enter new name: ");
    scanf(" %[^\n]", name);

    printf("Enter new email: ");
    scanf("%s", email);


    const char *query =
        "UPDATE students "
        "SET name = $1, email = $2 "
        "WHERE id = $3";


    char id_string[20];

    snprintf(
        id_string,
        sizeof(id_string),
        "%d",
        student->id
    );


    const char *values[3] = {
        name,
        email,
        id_string
    };


    PGresult *result =
        PQexecParams(
            conn,
            query,
            3,
            NULL,
            values,
            NULL,
            NULL,
            0
        );


    if (PQresultStatus(result) != PGRES_COMMAND_OK) {

        fprintf(stderr,
                "Profile update failed: %s\n",
                PQerrorMessage(conn));

        PQclear(result);
        return;
    }


    strcpy(student->name, name);
    strcpy(student->email, email);

    printf("\nProfile updated successfully.\n");

    PQclear(result);
}


/* ================================
   REGISTER COURSE
   ================================ */

void register_course(PGconn *conn,
                     Student student) {

    char course[100];

    printf("\n===== COURSE REGISTRATION =====\n");

    printf("Enter course name: ");
    scanf(" %[^\n]", course);


    char id_string[20];

    snprintf(
        id_string,
        sizeof(id_string),
        "%d",
        student.id
    );


    const char *query =
        "INSERT INTO courses "
        "(student_id, course_name) "
        "VALUES ($1, $2)";


    const char *values[2] = {
        id_string,
        course
    };


    PGresult *result =
        PQexecParams(
            conn,
            query,
            2,
            NULL,
            values,
            NULL,
            NULL,
            0
        );


    if (PQresultStatus(result) != PGRES_COMMAND_OK) {

        fprintf(stderr,
                "Course registration failed: %s\n",
                PQerrorMessage(conn));

        PQclear(result);
        return;
    }


    printf(
        "Course '%s' registered successfully.\n",
        course
    );

    PQclear(result);
}


/* ================================
   VIEW GRADES
   ================================ */

void view_grades(PGconn *conn,
                 Student student) {

    char id_string[20];

    snprintf(
        id_string,
        sizeof(id_string),
        "%d",
        student.id
    );


    const char *query =
        "SELECT course, grade "
        "FROM grades "
        "WHERE student_id = $1";


    const char *values[1] = {
        id_string
    };


    PGresult *result =
        PQexecParams(
            conn,
            query,
            1,
            NULL,
            values,
            NULL,
            NULL,
            0
        );


    if (PQresultStatus(result) != PGRES_TUPLES_OK) {

        fprintf(stderr,
                "Could not retrieve grades: %s\n",
                PQerrorMessage(conn));

        PQclear(result);
        return;
    }


    printf("\n===== GRADES =====\n");

    if (PQntuples(result) == 0) {

        printf("No grades available.\n");

    } else {

        for (int i = 0;
             i < PQntuples(result);
             i++) {

            printf(
                "%s : %s\n",
                PQgetvalue(result, i, 0),
                PQgetvalue(result, i, 1)
            );
        }
    }


    PQclear(result);
}