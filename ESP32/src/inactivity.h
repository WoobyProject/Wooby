extern unsigned long lastTimeActivity;
extern RTC_RODATA_ATTR int test;

extern void print_wakeup_reason();
extern void setUpInactivity();
extern void handleActionInactivity();
extern void inactivityCheck();
extern void RTC_IRAM_ATTR esp_wake_deep_sleep(void);