/********************************************************
42 Robot Car Controller (Logitech G27)
Special Thanks to HIDAPI and Feral Interactive
********************************************************/

#include <stdio.h>
#include <wchar.h>
#include <string.h>
#include <stdlib.h>
#include "hidapi.h"

// Headers needed for sleeping.
#include <unistd.h>


//Constants for using curl
char *ip = "192.168.2.3";
char *datturn[3] = {"/lf", "/st85", "/rt"};
char *datdir[2] = {"/rev", "/fwd"};

//Header for time
#include <time.h>

clock_t t0 = 0;

//This function allows

void	parse(unsigned char buf[256])
{
	unsigned char		gear;
	unsigned char		temp;
	unsigned short	wheel;
	int							turn;
	int							dir;
	int							on;
	clock_t					t1;

	printf("---Current State---\n");

	//Get Direction
	wheel = buf[3] + buf[4] * 256;
	printf("Turn angle: %.1f\nDirection: ", (wheel - 32767.0) / 65535.0 * 360.0);
	if (wheel < 0x7b00)
	{
		printf("left\n");
		turn = 0;
	}
	else if (wheel > 0x8300)
	{
		printf("right\n");
		turn = 2;
	}
	else
	{
		printf("straight\n");
		turn = 1;
	}

	//Get Gear
	temp = buf[2];
	gear = 0;
	while (temp){
		temp /= 2;
		gear++;
	}
	if (gear == 6)
	{
		dir = 0;
		printf("Gear set to R\n");
	}
	else
	{
		dir = 1;
		printf("Gear set to %d\n", gear);
	}

	//Check gas pedal
	if (buf[5] < 0xff){
		on = 1;
		printf("Gas is on\n");
	}
	else{
		on = 0;
		printf("Gas is off\n");
	}

	//Check brake pedal
	if (buf[6] < 0xff) {
		on &= 0;
		printf("Brake is on\n");
	}
	else{
		on &= 1;
		printf("Brake is off\n");
	}

	//Send command to car...
	t1 = clock();
	if (on && (t1 - t0) > 500)
	{
		char command[128] = "curl ";
		strcat(command, ip);
		strcat(command, datdir[dir]);
		strcat(command, datturn[turn]);
		system(command);
		t0 = clock();
	}
//	else
//		printf("no command... are you pressing the gas?\n");

	printf("--------------------\n");
}

int main(void)
{
	int 					res;
	unsigned char buf[256];
	#define MAX_STR 255
	wchar_t 			wstr[MAX_STR];
	hid_device 		*handle;
	int 					i;
	time_t				timer;

	struct hid_device_info *devs, *cur_dev;

	if (hid_init())
		return -1;

	// Set up the command buffer.
	memset(buf,0x00,sizeof(buf));
	buf[0] = 0x01;
	buf[1] = 0x81;


	// Open the device using the VID, PID,
	// and optionally the Serial number.
	////handle = hid_open(0x4d8, 0x3f, L"12345");
	handle = hid_open(0x046d, 0xc29b, NULL);
	if (!handle) {
		printf("unable to open device\n");
 		return 1;
	}

	// Read the Product String
	wstr[0] = 0x0000;
	res = hid_get_product_string(handle, wstr, MAX_STR);
	if (res < 0)
		printf("Unable to read product string\n");
	printf("Product String: %ls\n", wstr);

	// Set the hid_read() function to be non-blocking.
	hid_set_nonblocking(handle, 1);

	// Try to read from the device. There shoud be no
	// data here, but execution should not block.
	res = hid_read(handle, buf, 17);

	memset(buf,0,sizeof(buf));

	printf("Reading input...\n");

	// Read requested state. hid_read() has been set to be
	// non-blocking by the call to hid_set_nonblocking() above.
	// This loop demonstrates the non-blocking nature of hid_read().
	while (1)
	{
		res = 0;
		while (res == 0) {
			res = hid_read(handle, buf, sizeof(buf));
			if (res < 0)
				printf("Unable to read()\n");
		}

//		printf("Data read:\n");
//		// Print out the returned buffer.
//		for (i = 0; i < res; i++)
//			printf("buf[%d] = %02hhx \n", i, buf[i]);
		parse(buf);
		usleep(1000);
	}
	hid_close(handle);

	/* Free static HIDAPI objects. */
	hid_exit();

	return 0;
}
