#include <Arduino.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <Adafruit_NeoPixel.h>

// [수정] ESP32-S3-DevKitC-1 최적화 설정
#define LED_PIN     48    // 외부 스트립 연결 시 추천 (내장 LED 테스트 시 48)
#define NUM_PIXELS  1    // USB 전원 안정성을 고려한 권장 개수
#define BRIGHTNESS  25    // 전력 소모를 줄이기 위해 밝기 제한 (최대 255)

Adafruit_NeoPixel strip(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

void ledRainbowTask(void *pvParameters) {
    uint32_t firstPixelHue = 0;
    for (;;) {
        // 무지개 효과 (밀도를 높여 30개 LED에서도 자연스럽게 표현)
        strip.rainbow(firstPixelHue, 1, 255, 255, true);
        strip.show();

        firstPixelHue += 256; // 색상 회전 속도
        vTaskDelay(pdMS_TO_TICKS(20)); // 약 50 FPS
    }
}

void setup() {
    Serial.begin(115200);
    
    // N16R8 전용 PSRAM 확인
    if (psramInit()) {
        Serial.printf("N16R8 PSRAM Ready: %d bytes\n", ESP.getPsramSize());
    }

    strip.begin();
    strip.setBrightness(BRIGHTNESS);
    strip.show();

    // Core 1에서 실행 (애플리케이션 전용 코어)
    xTaskCreatePinnedToCore(
        ledRainbowTask, "RainbowTask", 4096, NULL, 1, NULL, 1
    );

    Serial.println("ESP32-S3 LED Test Start!");
}

void loop() {
    // 메인 루프는 비워두거나 다른 센서 로직을 추가할 수 있습니다.
    vTaskDelay(pdMS_TO_TICKS(1000));
}