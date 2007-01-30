#include <unistd.h>

#define REALPATH "/usr/local/bin/logview.pl"

int main (int argc, char** argv)
{
  execv(REALPATH, argv);
}
