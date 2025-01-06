#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

int gdb_console_redirect(int tty_num)
{
   char tty_name[16];
   snprintf(tty_name, sizeof(tty_name), "%s%1d", "/dev/ttyp", tty_num);

   int fd = open(tty_name, O_RDWR);
   if(fd < 0){
      printf("open %s failed: %d!\n", tty_name, fd);
      return -1;
   }

   printf("redirect TTY to %s\n", tty_name);
   dup2(fd, 0);
   dup2(fd, 1);
   dup2(fd, 2);
   return 0;
}
