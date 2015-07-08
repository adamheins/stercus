#include <stdio.h>
#include <stdlib.h>

int main() {
unsigned char *d = (unsigned char *)calloc(10000, 1);
d[0] = 100;
d[1] = 3;
while(1){
if(!d[0]){break;}
d[2] = d[1];
while(1){
if(!d[2]){break;}
d[0]--;
d[2]--;
}
d[3]++;
}
putchar(d[3]);
return 0;
}