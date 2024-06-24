
// Pin definition
const int pwmPin1 = 6; // PWM backward/forward
const int pwmPin2 = 5; // PWM right/left
const int pinX = A0; // X axis joystick
const int pinY = A1; // Y axis joystick
const int pinControl1 = 3; // Switch backward/forward
const int pinControl2 = 10; // Switch right/left

// Pins for the HC_SR04
const int PinTrig1 = 12;
const int PinEcho1 = 13;
const int PinTrig2 = 8;
const int PinEcho2 = 9;


// Sound speed in cm/s
const float VelSon = 34000.0;

bool stopCommandReceived = false;

float distancia1, distancia2;

// joystick added just in case it  is needed

enum Mode { NONE, EYE, VOICE, MOVEMENT, JOYSTICK, STOP };
Mode currentMode = STOP;

// Velocidad predeterminada
int velocidad_fija = 20;

void move_backward() {
    analogWrite(pwmPin1, velocidad_fija); 
    digitalWrite(pinControl1, HIGH); 
}

void move_forward() {
    analogWrite(pwmPin1, velocidad_fija); 
    digitalWrite(pinControl1, LOW); 
}

void move_left() {
    analogWrite(pwmPin2, velocidad_fija); 
    digitalWrite(pinControl2, LOW); 
}

void move_right() {
    analogWrite(pwmPin2, velocidad_fija); 
    digitalWrite(pinControl2, HIGH); 
}

void move_stop() {
    analogWrite(pwmPin1, 100);
    analogWrite(pwmPin2, 100); 
    digitalWrite(pinControl1, LOW); 
    digitalWrite(pinControl2, LOW); 
}

void iniciarTrigger() {
    digitalWrite(PinTrig1, LOW);
    delayMicroseconds(2);
    digitalWrite(PinTrig1, HIGH);
    delayMicroseconds(10);
    digitalWrite(PinTrig1, LOW);
}

void medirDistancia(int trigPin, int echoPin) {
    iniciarTrigger(trigPin);
    unsigned long tiempo = pulseIn(echoPin, HIGH);
    return tiempo * 0.000001 * VelSon / 2.0;
}

void setup() {
    Serial.begin(9600); // Serial comunication

    // Pin configuration for the HC_SR04
    pinMode(PinTrig1, OUTPUT);
    pinMode(PinEcho1, INPUT);
    pinMode(PinTrig2, OUTPUT);
    pinMode(PinEcho2, INPUT);


    pinMode(pwmPin1, OUTPUT);
    pinMode(pwmPin2, OUTPUT);
    pinMode(pinX, INPUT);
    pinMode(pinY, INPUT);
    pinMode(pinControl1, OUTPUT);
    pinMode(pinControl2, OUTPUT);

    move_stop(); // Stop as defect command
}

void loop() {
    iniciarTrigger();

    distancia1 = medirDistancia(PinTrig1, PinEcho1);
    distancia2 = medirDistancia(PinTrig2, PinEcho2);
    distancia3 = medirDistancia(PinTrig3, PinEcho3);
    distancia4 = medirDistancia(PinTrig4, PinEcho4);

    if (distancia1 < 20 || distancia2 < 20 || distancia3 < 20 || distancia4 < 20) {
        Serial.println("¡ALERTA! Objeto detectado a menos de 20 cm.");
        move_stop();
        return;
    }
    
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n'); 
        
        char cmd = command.charAt(0);
        
        switch (cmd) {
            case 'y':
                move_stop();
                stopCommandReceived = true; 
                break;

            case 'c':
                velocidad_fija = 1; // Establecer velocidad a 1
                Serial.println("Velocidad establecida a 1");
                stopCommandReceived = false; // Reanudar control
                break;
            case 'x':
                velocidad_fija = 7; // Establecer velocidad a 7
                Serial.println("Velocidad establecida a 7");
                stopCommandReceived = false; // Reanudar control
                break;
            case 'z':
                velocidad_fija = 12; // Establecer velocidad a 12
                Serial.println("Velocidad establecida a 12");
                stopCommandReceived = false; // Reanudar control
                break;
            case 't':
                currentMode = STOP;
                stopCommandReceived = false; // Reanudar control
                break;  
            case 'j':
                currentMode = JOYSTICK;
                stopCommandReceived = false; // Reanudar control
                break;
            case 'v':
                currentMode = VOICE;
                stopCommandReceived = false; // Reanudar control
                break; 
            case 'o':
                currentMode = EYE;
                stopCommandReceived = false; // Reanudar control
                if (distancia1 < 20) {
                    Serial.println("¡ALERTA! Objeto detectado a menos de 20 cm.");
                    move_stop();
                }
                break; 
            case 'm': // Modo de movimiento
                currentMode = MOVEMENT;
                stopCommandReceived = false; // Reanudar control
                break;
            case 'a':
                if (!stopCommandReceived) {
                    move_forward(); 
                    Serial.println("Moving Forward");
                }
                break;
            case 'b':
                if (!stopCommandReceived) {
                    move_backward();            
                    Serial.println("Moving Backward");
                }
                break;
            case 'l':
                if (!stopCommandReceived) {
                    move_left(); 
                    Serial.println("Moving Left");
                }
                break;
            case 'r':
                if (!stopCommandReceived) {
                    move_right(); 
                    Serial.println("Moving Right");
                }
                break;
            case 'p':
                move_stop();
                Serial.println("Stop");
                stopCommandReceived = false; // Reanudar control
                break;   
            default:
                break;
        }
    }

    if (!stopCommandReceived) {
        switch (currentMode) {
            case JOYSTICK:
                handle_joystick(); 
                break;
            case STOP:
                move_stop(); 
                break;
            case VOICE:
                handle_voice(); 
                break;
            case MOVEMENT:
                handle_movement(); 
                break;
            case EYE:
                break;
            default:
                break;
        }
    }
}

void handle_joystick() {
    int xValue = analogRead(pinX); 
    int yValue = analogRead(pinY); 

    if (yValue > 400 && yValue < 600 && xValue < 600 && xValue > 500) {
        move_stop();
    } else if (yValue > 1000 && xValue < 700 && xValue > 300) {
        move_backward(); 
    } else if (yValue < 100 && xValue < 700 && xValue > 300) {
        move_forward(); 
    } else if (xValue < 50 && yValue < 700 && yValue > 300) {
        move_left(); 
    } else if (xValue > 1000 && yValue < 700 && yValue > 300) {
        move_right(); 
    }
}

void handle_voice() {
    if (Serial.available() > 0) {
        String voiceCommand = Serial.readStringUntil('\n');
        voiceCommand.trim();
        
        if (voiceCommand.equalsIgnoreCase("a")) {
            move_forward();
            Serial.println("Moving Forward");
        } else if (voiceCommand.equalsIgnoreCase("b")) {
            move_backward();
            Serial.println("Moving Backward");
        } else if (voiceCommand.equalsIgnoreCase("l")) {
            move_left();
            Serial.println("Moving Left");
        } else if (voiceCommand.equalsIgnoreCase("r")) {
            move_right();
            Serial.println("Moving Right");
        } else if (voiceCommand.equalsIgnoreCase("p")) {
            move_stop();
            Serial.println("Stop");
        } else if (voiceCommand.equalsIgnoreCase("y")) {
            move_stop();
            stopCommandReceived = true; 
            Serial.println("Stop by command 'y'");
        }
    }
}

void handle_movement() {

}

