#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void win() {
    char *flag = getenv("FLAG");
    if (flag) {
        printf("Congratulations! Here is your flag: %s\n", flag);
    } else {
        printf("Flag not found! Ensure the FLAG environment variable is set.\n");
    }

    system("/bin/sh");
}

void vuln() {
    char buffer[64];
    printf("Input: ");
    gets(buffer);
}

int main() {
    setbuf(stdout, NULL);
    printf("Welcome to the CTF challenge!\n");
    vuln();
    return 0;
}