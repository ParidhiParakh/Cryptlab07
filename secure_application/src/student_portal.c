#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>

MYSQL *conn;

void connect_database()
{
    conn = mysql_init(NULL);

    if (conn == NULL)
    {
        printf("MySQL initialization failed.\n");
        exit(1);
    }

    if (mysql_real_connect(conn,
                           "localhost",
                           "root",
                           "password",
                           "student_portal",
                           3306,
                           NULL,
                           0) == NULL)
    {
        printf("Database connection failed: %s\n",
               mysql_error(conn));
        exit(1);
    }

    printf("Database connected successfully.\n");
}


/* ---------------- LOGIN ---------------- */


int login()
{
    char username[50];
    char password[50];
    char query[300];

    printf("\n===== LOGIN =====\n");

    printf("Username: ");
    scanf(" %[^\n]", username);

    printf("Password: ");
    scanf(" %[^\n]", password);

    /*
       INTENTIONALLY VULNERABLE:
       SQL Injection
    */

    sprintf(query,
            "SELECT * FROM students WHERE username='%s' AND password='%s'",
            username,
            password);

    printf("\nExecuting query: %s\n", query);

    if (mysql_query(conn, query))
    {
        printf("Query failed: %s\n", mysql_error(conn));
        return 0;
    }

    MYSQL_RES *result = mysql_store_result(conn);

    if (result == NULL)
    {
        return 0;
    }

    if (mysql_num_rows(result) > 0)
    {
        printf("Login successful!\n");
        mysql_free_result(result);
        return 1;
    }

    printf("Invalid username or password.\n");

    mysql_free_result(result);

    return 0;
}

/* ---------------- REGISTER ---------------- */

void register_student()
{
    char username[50];
    char password[50];
    char name[100];
    char email[100];

    char query[500];

    printf("\n===== STUDENT REGISTRATION =====\n");

    printf("Username: ");
    scanf("%49s", username);

    printf("Password: ");
    scanf("%49s", password);

    printf("Name: ");
    scanf("%99s", name);

    printf("Email: ");
    scanf("%99s", email);

    /*
       INTENTIONALLY VULNERABLE:
       SQL Injection
    */

    sprintf(query,
            "INSERT INTO students(username,password,name,email,grade) "
            "VALUES('%s','%s','%s','%s','N/A')",
            username,
            password,
            name,
            email);

    if (mysql_query(conn, query))
    {
        printf("Registration failed: %s\n", mysql_error(conn));
        return;
    }

    printf("Student registered successfully.\n");
}


/* ---------------- VIEW COURSES ---------------- */

void view_courses()
{
    MYSQL_RES *result;
    MYSQL_ROW row;

    printf("\n===== AVAILABLE COURSES =====\n");

    if (mysql_query(conn,
                    "SELECT id, course_name FROM courses"))
    {
        printf("Query failed.\n");
        return;
    }

    result = mysql_store_result(conn);

    while ((row = mysql_fetch_row(result)))
    {
        printf("%s - %s\n", row[0], row[1]);
    }

    mysql_free_result(result);
}


/* ---------------- REGISTER COURSE ---------------- */

void register_course(int student_id)
{
    int course_id;
    char query[200];

    view_courses();

    printf("\nEnter Course ID: ");
    scanf("%d", &course_id);

    /*
       INTENTIONALLY VULNERABLE:
       Missing validation/authorization
    */

    sprintf(query,
            "INSERT INTO registrations(student_id,course_id) "
            "VALUES(%d,%d)",
            student_id,
            course_id);

    if (mysql_query(conn, query))
    {
        printf("Course registration failed: %s\n",
               mysql_error(conn));
        return;
    }

    printf("Course registered successfully.\n");
}


/* ---------------- VIEW GRADES ---------------- */

void view_grades(int student_id)
{
    char query[300];

    /*
       INTENTIONALLY VULNERABLE:
       IDOR / Missing Authorization

       The function accepts student_id directly.
    */

    sprintf(query,
            "SELECT name, grade FROM students WHERE id=%d",
            student_id);

    if (mysql_query(conn, query))
    {
        printf("Query failed.\n");
        return;
    }

    MYSQL_RES *result = mysql_store_result(conn);
    MYSQL_ROW row;

    if ((row = mysql_fetch_row(result)))
    {
        printf("\nStudent: %s\n", row[0]);
        printf("Grade: %s\n", row[1]);
    }
    else
    {
        printf("Student not found.\n");
    }

    mysql_free_result(result);
}


/* ---------------- UPDATE PROFILE ---------------- */

void update_profile(int student_id)
{
    char name[100];
    char email[100];
    char query[300];

    printf("\n===== UPDATE PROFILE =====\n");

    printf("New name: ");
    scanf("%99s", name);

    printf("New email: ");
    scanf("%99s", email);

    /*
       INTENTIONALLY VULNERABLE:
       SQL Injection + unsafe string construction
    */

    sprintf(query,
            "UPDATE students SET name='%s', email='%s' WHERE id=%d",
            name,
            email,
            student_id);

    if (mysql_query(conn, query))
    {
        printf("Profile update failed: %s\n",
               mysql_error(conn));
        return;
    }

    printf("Profile updated successfully.\n");
}


/* ---------------- MAIN MENU ---------------- */

void student_menu(int student_id)
{
    int choice;

    while (1)
    {
        printf("\n============================\n");
        printf("       STUDENT PORTAL\n");
        printf("============================\n");

        printf("1. View Courses\n");
        printf("2. Register Course\n");
        printf("3. View Grades\n");
        printf("4. Update Profile\n");
        printf("5. Logout\n");

        printf("Enter choice: ");
        scanf("%d", &choice);

        switch (choice)
        {
            case 1:
                view_courses();
                break;

            case 2:
                register_course(student_id);
                break;

            case 3:
                view_grades(student_id);
                break;

            case 4:
                update_profile(student_id);
                break;

            case 5:
                printf("Logged out.\n");
                return;

            default:
                printf("Invalid choice.\n");
        }
    }
}


/* ---------------- MAIN ---------------- */

int main()
{
    int choice;
    int logged_in;

    connect_database();

    while (1)
    {
        printf("\n============================\n");
        printf("       STUDENT PORTAL\n");
        printf("============================\n");

        printf("1. Login\n");
        printf("2. Register\n");
        printf("3. Exit\n");

        printf("Enter choice: ");
        scanf("%d", &choice);

        switch (choice)
        {
            case 1:

                logged_in = login();

                if (logged_in)
                {
                    /*
                       For demonstration, Alice's ID is 1.
                    */
                    student_menu(1);
                }

                break;

            case 2:
                register_student();
                break;

            case 3:
                mysql_close(conn);
                printf("Goodbye!\n");
                return 0;

            default:
                printf("Invalid choice.\n");
        }
    }

    return 0;
}