#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./recover IMAGE\n");
        return 1;
    }
    FILE *file = fopen(argv[1], "r");

    if (file == NULL)
    {
        printf("Counld not open file\n");
        return 2;
    }

    unsigned char buffer[512];
    int count_image = 0;

    //pointer for recovered images
    FILE *output_file = NULL;
    
    char *filename = malloc(8 * sizeof(char));

    //reads blocks of 512 bytes
    while (fread(buffer, sizeof(char), 512, file))
    {
        //check the first bytes to see if it indicates a JPEG
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            sprintf(filename, "%03i.jpg", count_image);

            output_file = fopen(filename, "w");

            //count number of images found
            count_image++;
        }
        //check output for valid inpurt
        if (output_file != NULL)
        {
            fwrite(buffer, sizeof(char), 512, output_file);
        }
    }
    free(filename);
    fclose(output_file);
    fclose(file);

    return 0;
}