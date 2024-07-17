#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <math.h>

int count_letters(string text);

int count_words(string text);

int count_sentences(string text);

int main(void)
{
    string text = get_string("Text: ");

    int letters = count_letters(text);

    int words = count_words(text);

    int sentences = count_sentences(text);

    //calculates the index value by casting the ints as floats then back to an int
    float l = ((float)letters / (float)words) * 100;
    float s = ((float)sentences / (float)words) * 100;
    float cl_index = (0.0588 * l) - (0.296 * s) - 15.8;
    int r_index = round(cl_index);


    if (r_index >= 16)
    {
        printf("Grade 16+\n");
    }
    else if (r_index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", r_index);
    }
}

int count_letters(string text)
{
    int j = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (isalpha(text[i]))
        {
            j++;
        }
    }
    return j;
}

int count_words(string text)
{
    int j = 1;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (isspace(text[i]))
        {
            j++;
        }
    }
    return j;
}

int count_sentences(string text)
{
    int j = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            j++;
        }
    }
    return j;
}