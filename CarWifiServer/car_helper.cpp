#include "car_helper.h"

////////////////////////////////////////////////////////////////////////////////
//
////////////////////////////////////////////////////////////////////////////////
Servo myservo;
int speed;
int angle;
int m;
int straight;
int left;
int right;

int expire;
unsigned long start_time;
unsigned long ignore_time;
unsigned long ignored_cnt;
int flag;

dir_t current_state;
dir_t curr_request;
////////////////////////////////////////////////////////////////////////////////
//
////////////////////////////////////////////////////////////////////////////////

// int extract(char *s, char *kwd) {
// 	return atoi(s + String(kwd).length());
// }

// int check(char *s, char *kwd, int *param) {
// 	if (String(s).startsWith(kwd)) {
// 		*param = extract(s, kwd);
// 		Serial.println(String(kwd) + ": " + String(*param));
// 		return 1;
// 	}
// 	return 0;
// }

#define IS_DIGIT(x)   (x >= '0' && x <= '9')

dir_t parse_request(String &req) {
	dir_t ret_dir = {0, 0};
	int index;
	int val;

	// Steering Angle set
	if ((index = req.indexOf("/lf")) != -1){
		ret_dir.l_r = -1;
		index += String("/lf").length();
    // if (!(val = atoi(req.c_str() + index)) && req.c_str()[index] != '0')
		// 	val = 0;
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0)
				left = val;
		}
	}
	if ((index = req.indexOf("/rt")) != -1) {
		ret_dir.l_r = 1;
		index += String("/rt").length();
    // if (!(val = atoi(req.c_str() + index)) && req.c_str()[index] != '0')
		// 	val = 0;
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0)
				right = val;
		}
	}
	// angle += val * -1 * ret_dir.l_r; // adjust angle the wheel
	// if (angle > 120) angle = 120;
	// else if (angle < 30) angle = 30;
	// if (angle < straight)
	// 	ret_dir.l_r = 1;
	// if (angle > straight)
	// 	ret_dir.l_r = -1;

	if ((index = req.indexOf("/st")) != -1) {
		index += String("/st").length();
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0) {
				straight = val;
				// angle = straight;
				// ret_dir.l_r = 0;
			}
		}
	}

	// Expire period set
	if ((index = req.indexOf("/exp")) != -1) {
		index += String("/exp").length();
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0)
				expire = val;
		}
	}

	if ((index = req.indexOf("/m")) != -1) {
		index += String("/m").length();
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 150 && val <= 255)
				m = val;
		}
	}

	// Motor speed / direction set
	if ((index = req.indexOf("/fwd")) != -1) {
		ret_dir.f_r = 1;
		index += String("/fwd").length();
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0)
				m = val;
		}
	}
	if ((index = req.indexOf("/rev")) != -1) {
		ret_dir.f_r = -1;
		index += String("/rev").length();
		if ((val = atoi(req.c_str() + index)) || req.c_str()[index] == '0') {
			if (val >= 0)
				m = val;
		}
	}
	return ret_dir;
}

void send_accept(WiFiClient &client, dir_t &dir) {
	String s = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n";
	s += "<!DOCTYPE HTML>\r\n<html>\r\n<br>";
	s += "IR: " + String(digitalRead(IR)) + "\r\n<br>";
	s += "old left/right: " + String(current_state.l_r) + "\r\n<br>";
	s += "old forward/reverse: " + String(current_state.f_r) + "\r\n<br>";
	s += "straight(def 75(min 30, max 120)): " + String(straight) + "\r\n<br>";
	s += "left/right max/min (120/30): " + String(left) + " " + String(right) + "\r\n<br>";
	s += "new left/right: " + String(dir.l_r) + "\r\n<br>";
	s += "new forward/reverse: " + String(dir.f_r) + "\r\n<br>";
	s += "Speed: " + String(m) + "\r\n<br>";
	s += "expire: " + String(expire) + "\r\n";
	s += "</html>\n";
	client.flush();
	client.print(s);
	// Serial.println("Client disconnected");
}

void set_direction(dir_t &dir) {
	if (dir.l_r == -1) {
		myservo.write(left);
		Serial.println("Steering angle: left");
	}
	if (dir.l_r == 0) {
		myservo.write(straight);
		Serial.println("Steering angle: straight");
	}
	if (dir.l_r == 1) {
		myservo.write(right);
		Serial.println("Steering angle: right");
	}
	// myservo.write(angle);
}

void activate_motor(dir_t &dir) {
	if (dir.f_r == -1) {
		analogWrite(REV, m);
		Serial.println("PWM: forward");
	}
	if (dir.f_r == 1) {
		analogWrite(FWD, m);
		Serial.println("PWM: reverse");
	}
}

void deactivate_motor() {
	analogWrite(REV, LOW);
	analogWrite(FWD, LOW);
}
