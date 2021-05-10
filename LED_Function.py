from gpiozero import LED, Button

def LED_Function(GPIO_Number, event_wait, Program_Status_Code):

    # Link LED Output to GPIO pin number...
    led = LED(GPIO_Number)

    # Pause before pulsing status LED...
    event_wait.wait(2)

    # Pulse LED the same amount of times as program status code...
    for x in range(Program_Status_Code):

        led.on()
        event_wait.wait(0.4)
        print("LED On")

        led.off()
        event_wait.wait(0.4)
        print("LED Off")
