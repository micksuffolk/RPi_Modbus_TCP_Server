from gpiozero import LED, Button
#from time import sleep

def LED_Function(GPIO_Number, event_wait):

    led = LED(GPIO_Number)

    led.on()
    event_wait.wait(0.5)
    print("LED On")

    led.off()
    event_wait.wait(0.5)
    print("LED Off")
