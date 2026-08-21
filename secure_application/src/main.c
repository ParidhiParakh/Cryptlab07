#include <stdio.h>
#include "student.h"


void student_menu(PGconn *conn, Student *student) {

    int choice;

    while (1) {

        printf("\n==============================\n");
        printf("       STUDENT PORTAL\n");
        printf("==============================\n");
        printf("1. View Profile\n");
        printf("2. Update Profile\n");
        printf("3. Register Course\n");
        printf("4. View Grades\n");
        printf("5. Logout\n");
        printf("Enter choice: ");

        scanf("%d", &choice);

        switch (choice) {

            case 1:
                view_profile(conn, *student);
                break;

            case 2:
                update_profile(conn, student);
                break;

            case 3:
                register_course(conn, *student);
                break;

            case 4:
                view_grades(conn, *student);
                break;

            case 5:
                printf("\nLogged out successfully.\n");
                return;

            default:
                printf("\nInvalid choice.\n");
        }
    }
}


int main() {

    PGconn *conn;

    Student logged_in_student;

    int choice;


    /* Connect to PostgreSQL */

    conn = connect_db();

    if (conn == NULL) {

        printf("Unable to start Student Portal.\n");

        return 1;
    }


    /* Main menu */

    while (1) {

        printf("\n==============================\n");
        printf("       STUDENT PORTAL\n");
        printf("==============================\n");
        printf("1. Register\n");
        printf("2. Login\n");
        printf("3. Exit\n");
        printf("Enter choice: ");

        scanf("%d", &choice);


        switch (choice) {

            case 1:

                register_student(conn);

                break;


            case 2:

                if (login_student(
                        conn,
                        &logged_in_student)) {

                    student_menu(
                        conn,
                        &logged_in_student
                    );
                }

                break;


            case 3:

                printf("\nGoodbye!\n");

                close_db(conn);

                return 0;


            default:

                printf("\nInvalid choice.\n");
        }
    }


    close_db(conn);

    return 0;
}