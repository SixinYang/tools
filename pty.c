#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    int fd = open("/dev/ptmx", O_RDWR); // Open master side
    if (fd == -1) {
        perror("open ptmx failed");
        return 1;
    }

    printf("fd=%d\n", fd);
    char name[60];
    ptsname_r(fd, name, 60);
    printf("tty=%s\n", name);
    while(1){
    char c = getchar();
    printf("%c", c);
    write(fd, &c, 1); // Write to PTM
    }
    close(fd);
    return 0;
}

