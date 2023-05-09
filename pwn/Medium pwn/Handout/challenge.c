#include <stdio.h>
#include <string.h>

void function(char *str) {
    char buffer[16];
    strcpy(buffer, str);
    printf("Input: %s\n", buffer);
}

int main() {
    char input[32];
    printf("Enter a string:\n");
    fgets(input, 32, stdin);
    function(input);
    return 0;
}