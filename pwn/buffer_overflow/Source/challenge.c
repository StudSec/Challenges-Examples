#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void win() {
    char *flag = getenv("FLAG");
    while (*flag != 0x00) {
        putchar(*flag);
        flag += 1;
    }
    exit(0);
}

void vuln() {
    char buffer[64];
    printf("Input: ");
    gets(buffer);
}

int main() {
    setbuf(stdout, NULL);
    printf("Welcome to the CTF challenge! Win @ %p main @ %p\n", win, main);
    while (1) {
        vuln();
    }
    return 0;
}