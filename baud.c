#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <fcntl.h>

#define UART_BASE 0x02800000
#define UART_MDR1 (mapped_address + 0x20)
#define UART_LCR (mapped_address + 0x0c)
#define UART_DLH (mapped_address + 0x04)
#define UART_DLL (mapped_address + 0x00)

#define BYTE(addr, value) (*(volatile unsigned char *)(addr) = (value))
#define BIT(addr, mask, value) *(volatile unsigned char *)(addr) = ((*(volatile unsigned char *)(addr) & ~(mask)) | (value) & (mask))

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <baud_rate>\n", argv[0]);
        return 1;
    }

    int baud_rate = atoi(argv[1]);
    if (baud_rate <= 0) {
        fprintf(stderr, "Invalid baud rate: %s\n", argv[1]);
        return 1;
    }

    // Open /dev/mem to access physical memory
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        perror("Failed to open /dev/mem");
        return -1;
    }

    printf("Baud rate set to: %d\n", baud_rate);
    unsigned char* mapped_address = mmap(
        NULL,                       // Kernel selects the virtual address
        0x100,                // Size of the region
        PROT_READ | PROT_WRITE | PROT_NOCACHE,     // Read and write permissions
        MAP_SHARED | MAP_PHYS,      // Shared, physical memory mapping
        NOFD,
        UART_BASE               // Physical address to map
    );

    if (mapped_address == MAP_FAILED) {
        perror("mmap_device_memory failed");
        return -1;
    }

    BIT(UART_MDR1, 0x7, 0x7);
    BIT(UART_LCR, 0x80, 0x80);

    switch (baud_rate)
    {
    case 9600:
        BYTE(UART_DLH, 0x01);
        BYTE(UART_DLL, 0x39);
        break;
    case 115200:
        BYTE(UART_DLH, 0x00);
        BYTE(UART_DLL, 0x1a);
        break;
    case 230400:
        BYTE(UART_DLH, 0x00);
        BYTE(UART_DLL, 0x0d);
        break;
    
    default:
        break;
    }

    BIT(UART_LCR, 0x80, 0x00);
    BIT(UART_MDR1, 0x7, 0x0);

    if (munmap_device_memory(mapped_address, 0xb0) == -1) {
        perror("munmap_device_memory failed");
    }

    return 0;
}