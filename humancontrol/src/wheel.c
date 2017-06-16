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

//PID and VID for wheel
int	pid = 0xc29b;
int	vid = 0x046d;

//Constants for using curl
char *ip = "192.168.2.3";
char *datturn[3] = {"/hlf", "", "/hrt"};
char *datdir[2] = {"/rev", "/fwd"};

//Header for time
#include <time.h>

//Constants
#define MAX_STR 255
time_t timeout = 1;
float	angle = 90.0;

int	parse(unsigned char buf[256])
{
	unsigned char		gear;
	unsigned char		temp;
	unsigned short	wheel;
	float						steer;
	int							turn;
	int							dir;
	int							on;

//	printf("---Current State---\n");

	//Get Direction
	wheel = buf[3] + buf[4] * 256;
	steer = (wheel - 32767.0) / 65535.0 * angle;
//	printf("Turn angle: ");
	//if (steer > 45.0 || steer < -45.0)
	//	printf("\x1b[31m");
//	printf("%.1f\x1b[0m\nDirection: ", steer);
	if (steer < angle / -20)
	{
//		printf("left\n");
		turn = 0;
	}
	else if (steer > angle / 20)
	{
//		printf("right\n");
		turn = 2;
	}
	else
	{
//		printf("straight\n");
		turn = 1;
	}

	//Get Gear
	temp = buf[2];
	gear = 0;
	while (temp){
		temp /= 2;
		gear++;
	}
	if (gear == 0)
	{
		dir = 2;
//		printf("Gear set to N\n");
	}
	else if (gear % 2 == 0)
	//if (gear == 6)
	{
		dir = 0;
//		printf("Gear set to R\n");
	}
	else
	{
		dir = 1;
//		printf("Gear set to F\n");
		//printf("Gear set to %d\n", gear);
		//if (!gear)
		//	dir = 2;
	}

	//Check gas pedal
	if (buf[5] < 0xff){
		on = 1;
	}
	else{
		on = 0;
	}

	//Check brake pedal
	if (buf[6] < 0xff) {
		on &= 0;
	}
	else{
		on &= 1;
	}

	//Send command to car...
	//if (on && dir < 2)
	if (1)
	{
		char command[128];
		char num[4];

		memset(command, 0, 128);
//		strcat(command, ip);
		if (on && gear)
			strcat(command, datdir[dir]);
		strcat(command, datturn[turn]);
		if (turn != 1) {
			sprintf(num, "%.0f", (steer - 75) * (-1));
			strcat(command, num);
		}
		for (int i = 0; i < 128; i++)
		{
			if (!command[i])
				break;
			write(1, &command[i], 1);
		}
//		system(command);
		return (1);
	}
	//else
	//	printf("no command... are you pressing the gas?\n");

//	printf("-------------------\n");
	return (0);
}

int main(void)
{
	int 					res;
	unsigned char buf[256];
	wchar_t 			wstr[MAX_STR];
	hid_device 		*handle;
	int 					i;
	time_t 			start;

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
	handle = hid_open(vid, pid, NULL);
	if (!handle) {
		printf("unable to open device\n");
 		return (1);
	}

	// Read the Product String
	wstr[0] = 0x0000;
	res = hid_get_product_string(handle, wstr, MAX_STR);
//	if (res < 0)
//		printf("Unable to read product string\n");
//	printf("Product String: %ls\n", wstr);

	// Set the hid_read() function to be non-blocking.
	hid_set_nonblocking(handle, 1);

	// Try to read from the device. There shoud be no
	// data here, but execution should not block.
	res = hid_read(handle, buf, 17);

	memset(buf,0,sizeof(buf));

//	printf("Reading input...\n");

	// Read requested state. hid_read() has been set to be
	// non-blocking by the call to hid_set_nonblocking() above.
	// This loop demonstrates the non-blocking nature of hid_read().
	res = 0;
	start = time(NULL);
	while (res == 0 && time(NULL) - start < timeout) {
		res = hid_read(handle, buf, sizeof(buf));
//			if (res < 0)
//				printf("Unable to read()\n");
		}
	if (!res)
		return (0);
//		printf("Data read:\n");
//		// Print out the returned buffer.
//		for (i = 0; i < res; i++)
//			printf("buf[%d] = %02hhx \n", i, buf[i]);
	parse(buf);
	hid_close(handle);

	/* Free static HIDAPI objects. */
	hid_exit();

	return (0);
}
