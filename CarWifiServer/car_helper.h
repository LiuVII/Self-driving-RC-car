#ifndef CAR_HELPER_H
#define CAR_HELPER_H

#include <ESP8266WiFi.h>
#include <Servo.h>
#include <string.h>

typedef struct {
	int	l_r;
	int f_r;
} dir_t;

// Internet Settings
extern const char *ssid;
extern const char *password;
extern Servo myservo;

// Pins
#define IR				D0
#define SRV				D2
#define FWD				D3
#define REV				D4

#define M					150
#define LEFT 			120 // 100 @ 2sec
#define STRAIGHT	85
#define RIGHT			30 // 75 @ 2sec
extern int m;
extern int left;
extern int straight;
extern int right;

extern int h_lf;
extern int h_rt;
extern int h_st;

extern bool wheel;


#define IS_DIR_VAL(x)		(x.l_r || x.f_r)
#define ANGLE_VALID(x)	(x >= RIGHT && x <= LEFT)
#define SPEED_VALID(x)	(x >= 0 && x <= M)
#define TIME_VALID(x)		(x > 0 && x <= 1000)

// MOTOR PARAMETERS
extern int speed;
extern int angle;

extern int expire;
extern unsigned long start_time;
extern unsigned long ignore_time;
extern unsigned long ignored_cnt;
extern int flag;

extern dir_t current_state;
extern dir_t curr_request;

int extract(char *s, char *kwd);
int check(char *s, char *kwd, int *param);

dir_t parse_request(String &req);

void send_accept(WiFiClient &client, dir_t &dir);

void set_direction(dir_t &dir);
void set_hdirection(dir_t &dir);
void activate_motor(dir_t &dir);
void deactivate_motor();

#endif
