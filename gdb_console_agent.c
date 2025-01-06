#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

void reader(void *arg)
{
    char buff[64];
    int fd = (int)arg;

    while(1){
        unsigned int len = read(fd, buff, sizeof(buff));
        if(!len){
            printf("read closed\n");
            return;
        }
        for(int i=0; i<len; i++){
            putchar(buff[i]);
        }
    }
}

void writer(void *arg)
{
    int fd = (int)arg;

    while(1){
        int ret = getchar();
        if(ret == EOF){
            printf("writer closed\n");
            return;
        }

        char out = (char)ret;
        write(fd, &out, 1);
    }
}

void SetUpTerminalIOforCLI() 
{
    struct termios termio;
    struct termios orgin;
    struct termios orgout;
    
    (void)tcgetattr(0,&orgin);
    (void)tcgetattr(1,&orgout);

    // originalIn = orgin;
    // originalOut = orgout;
    
    termio = orgin;        
    termio.c_lflag &= ~(ICANON|ECHO);
    termio.c_cc[VMIN] = 1;
    termio.c_cc[VTIME] = 0;
    tcsetattr(0,TCSANOW,&termio);
    tcsetattr(1,TCSANOW,&termio);
}

int main(int argc, char *argv[])
{
    if(argc < 2){
        printf("Usage: %s <tty number>", argv[0]);
        return -1;
    }

    SetUpTerminalIOforCLI();
    
    char pts_name[16];
    snprintf(pts_name, sizeof(pts_name), "%s%s", "/dev/ptyp", argv[1]);
    int fd = open(pts_name, O_RDWR);
    if(fd < 0){
        printf("open %s failed: %d\n", pts_name, fd);
        return -1;
    }

    pthread_t workers[2];
    pthread_create(&workers[0], NULL, reader, fd);
    pthread_create(&workers[1], NULL, writer, fd);

    pthread_join(workers[0], NULL);
    pthread_join(workers[1], NULL);
    printf("EXIT\n");
    return 0;
}