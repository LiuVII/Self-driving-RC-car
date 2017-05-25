
gcc -framework IOKit -framework CoreFoundation -I includes wheel.c hid.c -o wheeltest
./wheeltest
