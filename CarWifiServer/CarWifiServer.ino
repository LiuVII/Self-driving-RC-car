#include "car_helper.h"

const char *ssid = "robotics";
const char *password = "rac3r00m";

WiFiServer server(80);
bool state;

void setup() {
	current_state = {0, 0};
	curr_request = {0, 0};

	m = M;	
	straight = STRAIGHT;
	left = LEFT;
	right = RIGHT;

	wheel = false;
	h_rt = RIGHT;
	h_st = STRAIGHT;
	h_lf = LEFT;
	// angle = straight;
	// speed = M;

	expire = 500;
	ignored_cnt = 0;

	state = false;

	Serial.begin(115200);
	delay(10);
	Serial.println("Serial Initiated");

	pinMode(FWD, OUTPUT);
	analogWrite(FWD, LOW);
	pinMode(REV, OUTPUT);
	analogWrite(REV, LOW);
	Serial.println("Pins Initiated");

	myservo.attach(SRV);
	Serial.println("Servo Attached");
	myservo.write(straight);

	Serial.println("Connecting to ");
	Serial.println(ssid);

	WiFi.begin(ssid, password);
	while(WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.print(".");
	}
	Serial.println("");
	Serial.println("WiFi Connected");

	server.begin();
	Serial.println("Server started");
	Serial.println(WiFi.localIP());
}

void loop() {
	WiFiClient client = server.available();
	bool client_avail = false;
	if (client) {
		client_avail = true;
		while (!client.available())
			delay(1);
	}
	String req = "";
	if (client) {
		req = String(client.readStringUntil('\r').c_str());
		client.flush();
		curr_request = parse_request(req);
		Serial.println(req);
		send_accept(client, curr_request);
		state = true;
	}
	if (!state){
		curr_request.l_r = 0;
		curr_request.f_r = 0;
	}
	int cur_time = millis();
  if (cur_time - start_time >= expire) { // uptick
  	Serial.println("uptick");
  	Serial.println("Curr_req: " + String(curr_request.l_r) + " " + String(curr_request.f_r));
  	Serial.println("Curr_state: " + String(current_state.l_r) + " " + String(current_state.f_r));
  	start_time = cur_time;
  	if (state) {
  		Serial.print("True");
  		if (current_state.f_r != curr_request.f_r)
  			deactivate_motor();
  		if (!wheel)
			set_direction(curr_request);
		else
			set_hdirection(curr_request);
  		if (curr_request.f_r)
  			activate_motor(curr_request);
  		ignored_cnt = 0;
  		current_state = curr_request;
  	} else {
  		Serial.print("False");
  		current_state.l_r = 0;
  		current_state.f_r = 0;
  		deactivate_motor();
  	}
  	Serial.println("new State: " + String(current_state.l_r) + " " + String(current_state.f_r));
  	state = false;
  } else {  // save the last client request
  	if (client_avail) {
			// Serial.println("igLast_req: " + String(last_request.l_r) + " " + String(last_request.f_r));
			// Serial.println("igCurr_req: " + String(curr_request.l_r) + " " + String(curr_request.f_r));
			// Serial.println("igCurr_state: " + String(current_state.l_r) + " " + String(current_state.f_r));
  		++ignored_cnt;
  	}
  }
}
