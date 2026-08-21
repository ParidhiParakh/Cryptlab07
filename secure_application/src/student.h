#ifndef STUDENT_H
#define STUDENT_H

#include <libpq-fe.h>

#define MAX_NAME 100
#define MAX_EMAIL 100
#define MAX_USERNAME 50
#define MAX_PASSWORD 100

typedef struct {
    int id;
    char name[MAX_NAME];
    char email[MAX_EMAIL];
    char username[MAX_USERNAME];
} Student;

/* Database connection */
PGconn *connect_db(void);
void close_db(PGconn *conn);

/* Student functions */
void register_student(PGconn *conn);
int login_student(PGconn *conn, Student *logged_in_student);
void view_profile(PGconn *conn, Student student);
void update_profile(PGconn *conn, Student *student);
void register_course(PGconn *conn, Student student);
void view_grades(PGconn *conn, Student student);

#endif