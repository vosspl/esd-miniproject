#include "config.h"
#include "esp_mac.h"
//#include <WiFi.h>
//#include <HTTPClient.h>

//const char* ssid = "NETGEAR28";
//const char* password = "elegantsea867";
//const char* serverURL = "http://192.168.1.2:5000/";

// Check if Bluetooth configs are enabled
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run make menuconfig to and enable it
#endif

const float STEP_LENGTH = 0.75; // Average step length in meters
float distance = 0.0;
uint32_t sessionStartTime = 0;
uint32_t sessionDuration = 0;
uint32_t sessionId = 0;

// Bluetooth Serial object
BluetoothSerial SerialBT;

// Watch objects
TTGOClass *watch;
TFT_eSPI *tft;
BMA *sensor;
TinyGPSPlus *gps;
bool irq = false;
uint32_t steps = 0;


uint32_t updateTimeout = 0;
uint32_t last = millis();
uint8_t baseMac[6];

volatile uint8_t state;
volatile bool irqBMA = false;
volatile bool irqButton = false;

bool sessionStored = false;
bool sessionSent = false;



void initHikeWatch()
{
    // LittleFS
    if(!LITTLEFS.begin(FORMAT_LITTLEFS_IF_FAILED)){
        Serial.println("LITTLEFS Mount Failed");
        return;
    }

    // Stepcounter

    // Configure IMU
    Acfg cfg;
    cfg.odr = BMA4_OUTPUT_DATA_RATE_100HZ;
    cfg.range = BMA4_ACCEL_RANGE_2G;
    cfg.bandwidth = BMA4_ACCEL_NORMAL_AVG4;
    cfg.perf_mode = BMA4_CONTINUOUS_MODE;
    sensor->accelConfig(cfg);
    sensor->enableAccel();
 
    // Enable BMA423 step count feature
    sensor->enableFeature(BMA423_STEP_CNTR, true);

    // Reset steps
    sensor->resetStepCounter();

    // Turn on step interrupt
    sensor->enableStepCountInterrupt();
    pinMode(BMA423_INT1, INPUT);
    attachInterrupt(BMA423_INT1, [] {
        // Set interrupt to set irq value to 1
        irq = 1;
    }, RISING); //It must be a rising edge

    // Side button
    pinMode(AXP202_INT, INPUT_PULLUP);
    attachInterrupt(AXP202_INT, [] {
        irqButton = true;
    }, FALLING);

    //!Clear IRQ unprocessed first
    watch->power->enableIRQ(AXP202_PEK_SHORTPRESS_IRQ, true);
    watch->power->clearIRQ();

    // GPS Initialization
    watch->trunOnGPS(); // Power on GPS module
    watch->gps_begin();
    gps = watch->gps;

    return;
}

void sendDataBT(fs::FS &fs, const char * path)
{
    /* Sends data via SerialBT */
    File file = fs.open(path);
    if(!file || file.isDirectory()){
        Serial.println("- failed to open file for reading");
        return;
    }
    Serial.println("- read from file:");
    while(file.available()){
        SerialBT.write(file.read());
    }
    file.close();
}

void sendSessionBT()
{
    // Read session and send it via SerialBT
    watch->tft->fillRect(0, 0, 240, 240, TFT_BLACK);
    watch->tft->drawString("Sending session", 20, 80);
    watch->tft->drawString("to Hub", 80, 110);

    // Sending session id
    sendDataBT(LITTLEFS, "/id.txt");
    SerialBT.write(';');
    // Sending steps
    sendDataBT(LITTLEFS, "/steps.txt");
    SerialBT.write(';');
    // Sending distance
    sendDataBT(LITTLEFS, "/distance.txt");
    SerialBT.write(';');
    // Send connection termination char
    SerialBT.write('\n');


}


void saveIdToFile(uint16_t id)
{
    char buffer[10];
    itoa(id, buffer, 10);
    writeFile(LITTLEFS, "/id.txt", buffer);
}

void saveStepsToFile(uint32_t step_count)
{
    char buffer[10];
    itoa(step_count, buffer, 10);
    writeFile(LITTLEFS, "/steps.txt", buffer);
}

void saveDistanceToFile(float distance)
{
    char buffer[10];
    itoa(distance, buffer, 10);
    writeFile(LITTLEFS, "/distance.txt", buffer);
}

void saveGPSToFile(double lat, double lng) {
    char buffer[50];
    snprintf(buffer, sizeof(buffer), "Lat: %.6f, Long: %.6f", lat, lng);
    writeFile(LITTLEFS, "/gps.txt", buffer);
  }

  void saveSessionTimeToFile(uint32_t duration)
  {
      char buffer[20];
      snprintf(buffer, sizeof(buffer), "%02d:%02d:%02d", duration / 3600, (duration % 3600) / 60, duration % 60);
      writeFile(LITTLEFS, "/session_time.txt", buffer);
  }

void deleteSession()
{
    deleteFile(LITTLEFS, "/id.txt");
    deleteFile(LITTLEFS, "/distance.txt");
    deleteFile(LITTLEFS, "/steps.txt");
    deleteFile(LITTLEFS, "/gps.txt");
}

void setup()
{
    Serial.begin(115200);
    watch = TTGOClass::getWatch();
    watch->begin();
    watch->openBL();

    //Receive objects for easy writing
    tft = watch->tft;
    sensor = watch->bma;
    
    initHikeWatch();
    watch -> trunOnGPS();
    state = 1;

    SerialBT.begin("Hiking Watch");
}

void loop()
{
    switch (state)
    {
    case 1:
    {
        /* Initial stage */
        //Basic interface
        watch->tft->fillScreen(TFT_BLACK);
        watch->tft->setTextFont(4);
        watch->tft->setTextColor(TFT_WHITE, TFT_BLACK);
        watch->tft->drawString("Hiking Watch",  45, 25, 4);
        watch->tft->drawString("Press button", 50, 80);
        watch->tft->drawString("to start session", 40, 110);

        bool exitSync = false;

        //Bluetooth discovery
        while (1)
        {
            /* Bluetooth sync */
            if (SerialBT.available())
            {
                tft->printf("1");
                char incomingChar = SerialBT.read();
                if (incomingChar == 'c' and sessionStored and not sessionSent)
                {
                    sendSessionBT();
                    sessionSent = true;
                    tft->printf("2");
                }

                if (sessionSent && sessionStored) {
                    // Update timeout before blocking while
                    updateTimeout = 0;
                    last = millis();
                    while(1)
                    {
                        updateTimeout = millis();

                        if (SerialBT.available())
                            incomingChar = SerialBT.read();
                        if (incomingChar == 'r')
                        {
                            Serial.println("Got an R");
                            // Delete session
                            deleteSession();
                            sessionStored = false;
                            sessionSent = false;
                            incomingChar = 'q';
                            exitSync = true;
                            break;
                        }
                        else if ((millis() - updateTimeout > 2000))
                        {
                            Serial.println("Waiting for timeout to expire");
                            updateTimeout = millis();
                            sessionSent = false;
                            exitSync = true;
                            break;
                        }
                    }
                }
            }
            if (exitSync)
            {
                delay(1000);
                watch->tft->fillRect(0, 0, 240, 240, TFT_BLACK);
                watch->tft->drawString("Hiking Watch",  45, 25, 4);
                watch->tft->drawString("Press button", 50, 80);
                watch->tft->drawString("to start session", 40, 110);
                exitSync = false;
            }

            /*      IRQ     */
            if (irqButton) {
                irqButton = false;
                watch->power->readIRQ();
                if (state == 1)
                {
                    state = 2;
                }
                watch->power->clearIRQ();
            }
            if (state == 2) {
                if (sessionStored)
                {
                    watch->tft->fillRect(0, 0, 240, 240, TFT_BLACK);
                    watch->tft->drawString("Overwriting",  55, 100, 4);
                    watch->tft->drawString("session", 70, 130);
                    delay(1000);
                }
                break;
            }
        }
        break;
    }
    case 2:
    {
        /* Hiking session initalisation */
        sessionId++;  // Increment session ID for each new session
        sensor->resetStepCounter();  
        steps = 0;
        distance = 0.0;
        sessionStartTime = millis();
        // Clear screen to prevent previous data from showing
        tft->fillScreen(TFT_BLACK);
        state = 3;
        break;
    }
    case 3:
    {
        /* Hiking session ongoing */

        watch->tft->fillRect(0, 0, 240, 240, TFT_BLACK);
        watch->tft->drawString("Starting hike", 45, 100);
        delay(1000);
        watch->tft->fillRect(0, 0, 240, 240, TFT_BLACK);
        while (state == 3) {  // Keep updating display
            watch->gpsHandler();  // Update GPS constantly

        //Calculate elapsed session time
        uint32_t elapsedTime = (millis() - sessionStartTime) / 1000;
        uint8_t hours = elapsedTime / 3600;
        uint8_t minutes = (elapsedTime % 3600) / 60;
        uint8_t seconds = elapsedTime % 60;

        //Update display every loop iteration
        tft->fillRect(5, 35, 230, 25, TFT_BLACK);  // Clear session ID
        tft->fillRect(5, 65, 230, 25, TFT_BLACK);  // Clear steps
        tft->fillRect(5, 95, 230, 25, TFT_BLACK);  // Clear distance
        tft->fillRect(5, 125, 230, 25, TFT_BLACK); // Clear GPS data
        tft->fillRect(5, 155, 230, 25, TFT_BLACK); // Clear session time

        // Set font and text size
        tft->setTextFont(2);
        tft->setTextColor(TFT_WHITE, TFT_BLACK);

        // Display session ID
        tft->setCursor(5, 35);
        tft->print("Session ID: ");
        tft->print(sessionId);

        // Display step count
        tft->setCursor(5, 65);
        tft->print("Steps: ");
        tft->print(steps);

        // Display distance
        tft->setCursor(5, 95);
        tft->print("Distance: ");
        tft->print(distance, 2);
        tft->print(" km");

        // Display GPS coordinates
        tft->setCursor(5, 125);
        tft->print("GPS: ");
        tft->print(gps->location.lat(), 6);
        tft->print(", ");
        tft->print(gps->location.lng(), 6);

        //Display session time
        tft->setCursor(5, 155);
        tft->print("Time: ");
        tft->printf("%02d:%02d:%02d", hours, minutes, seconds);
        

        //Update Step Count if Interrupt Triggered
        if (irq) {
            irq = false;
            while (!sensor->readInterrupt());

            if (sensor->isStepCounter()) {
                steps = sensor->getCounter();
                distance = (steps * STEP_LENGTH) / 1000.0;
            }
        }
        if (irqButton) {
            irqButton = false;
            watch->power->readIRQ();
            state = 4;
            watch->power->clearIRQ();
        }
            delay(500);
        }
        break;
    }
    case 4:
    {
        //Save hiking session data
        saveIdToFile(sessionId);
        saveStepsToFile(steps);
        saveDistanceToFile(distance);
        saveGPSToFile(gps->location.lat(), gps->location.lng());
        sessionStored = true;
        //sendSessionBT();

        delay(1000);
        state = 1;  
        break;
    }
    default:
        // Restart watch
        ESP.restart();
        break;
    }
}