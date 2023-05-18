#include <stdio.h>
#include <string.h>
#include <unistd.h>  //Used for UART
#include <fcntl.h>   //Used for UART
#include <termios.h> //Used for UART
#define TAMANHO_MATRICULA 4

int main(int argc, const char *argv[])
{

    int uart0_filestream = -1;

    uart0_filestream = open("/dev/serial0", O_RDWR | O_NOCTTY | O_NDELAY); // Open in non blocking read/write mode
    if (uart0_filestream == -1)
    {
        printf("Erro - Não foi possível iniciar a UART.\n");
    }
    else
    {
        printf("UART inicializada!\n");
    }
    struct termios options;
    tcgetattr(uart0_filestream, &options);
    options.c_cflag = B9600 | CS8 | CLOCAL | CREAD; //<Set baud rate
    options.c_iflag = IGNPAR;
    options.c_oflag = 0;
    options.c_lflag = 0;
    tcflush(uart0_filestream, TCIFLUSH);
    tcsetattr(uart0_filestream, TCSANOW, &options);

    unsigned int command;
    while (command)
    {
        printf("Digite o comando: ");
        scanf("%x", &command);

        unsigned int matricula[TAMANHO_MATRICULA] = {1, 6, 0, 2};
        unsigned char tx_buffer[260];
        unsigned char *p_tx_buffer;

        p_tx_buffer = &tx_buffer[0];

        memcpy(p_tx_buffer++, &command, 1);

        if (command == 0xB1)
        {
            int data;
            printf("Digite o inteiro a ser enviado.\n");

            scanf("%d", &data);

            memcpy(p_tx_buffer, &data, sizeof(data));
            p_tx_buffer += sizeof(data);
        }
        else if (command == 0xB2)
        {
            float data;
            printf("Digite o float a ser enviado.\n");

            scanf("%f", &data);

            memcpy(p_tx_buffer, &data, sizeof(data));
            p_tx_buffer += sizeof(data);
        }
        else if (command == 0xB3)
        {
            printf("Digite o tamanho da string a ser enviada.\n");
            int size;
            scanf("%d", &size);

            printf("Digite a string a ser enviada.\n");
            char data[256];

            scanf("%s", data);

            memcpy(p_tx_buffer++, &size, 1);
            memcpy(p_tx_buffer, &data[0], size);
            p_tx_buffer += size;
        }

        // for(int i =0;i<TAMANHO_MATRICULA; i++){}

        memcpy(p_tx_buffer++, &matricula[0], 1);
        memcpy(p_tx_buffer++, &matricula[1], 1);
        memcpy(p_tx_buffer++, &matricula[2], 1);
        memcpy(p_tx_buffer++, &matricula[3], 1);

        printf("Buffers de memória criados!\n");

        printf("Escrevendo caracteres na UART ...");

        int count = write(uart0_filestream, &tx_buffer[0], (p_tx_buffer - &tx_buffer[0]));
        if (count < 0)
        {
            printf("UART TX error\n");
        }
        else
        {
            printf("escrito.%d\n", count);
        }

        sleep(1);

        //----- CHECK FOR ANY RX BYTES -----
        // Read up to 255 characters from the port if they are there
        unsigned char rx_buffer[257];
        int rx_length = read(uart0_filestream, (void *)rx_buffer, 256); // Filestream, buffer to store in, number of bytes to read (max)
        if (rx_length < 0)
        {
            printf("Erro na leitura.\n"); // An error occured (will occur if there are no bytes)
        }
        else if (rx_length == 0)
        {
            printf("Nenhum dado disponível.\n"); // No data waiting
        }
        else
        {

            if (command >= 0xA1 && command <= 0xB1)
            {
                int data;
                memcpy(&data, rx_buffer, sizeof(data));

                printf("%i Bytes lidos : %d\n", rx_length, data);
            }
            else if (command >= 0xA2 && command <= 0xB2)
            {
                float data;
                memcpy(&data, rx_buffer, sizeof(data));

                printf("%i Bytes lidos : %f\n", rx_length, data);
            }
            else if (command >= 0xA3 && command <= 0xB3)
            {

                int dataSize;
                memcpy(&dataSize, rx_buffer, 1);

                char data[dataSize + 1];
                memcpy(&data, &rx_buffer[1], dataSize);

                data[dataSize] = '\0';

                printf("%i Bytes lidos : %s\n", rx_length, data);
            }
        }
    }

    close(uart0_filestream);
    return 0;
}
