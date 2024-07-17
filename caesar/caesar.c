#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

char rotate(char c, int n);

bool only_digits(string s);

int main(int argc, string argv[])
{
    //runs only if it has one command line and it is all numbers
    if (argc == 2 && only_digits(argv[1]))
    {
        int key = atoi(argv[1]);
        string text = get_string("plaintext: ");

        for (int i = 0, n = strlen(text); i < n; i++)
        {
            text[i] = rotate(text[i], key);
        }

        printf("ciphertext: %s\n", text);
        return 0;
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
}

char rotate(char c, int n)
{
    int numC = 0;
    if (isupper(c))
    {
        //brings brings the character down then increases by n and looping around when numC%26 ==0
        numC = c - 'A';
        for (int i = n; i > 0; i--)
        {
            numC++;
            if (numC % 26 == 0)
            {
                numC = numC - 26;
            }
        }
        c = (char) numC + 'A';
    }
    else if (islower(c))
    {
        numC = c - 'a';
        for (int i = n; i > 0; i--)
        {
            numC++;
            if (numC % 26 == 0)
            {
                numC = numC - 26;
            }
        }
        c = (char) numC + 'a';
    }
    else
    {
        return c;
    }
    return c;
}

bool only_digits(string s)
{
    for (int i = 0, n = strlen(s); i < n; i++)
    {
        if (isdigit(s[i]) == 0)
        {
            return 0;
        }
    }
    return 1;
}