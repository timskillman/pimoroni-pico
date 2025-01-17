# This example takes the temperature from the Pico's onboard temperature sensor, and displays it on Pico Display Pack, along with a little pixelly graph.
# It's based on the thermometer example in the "Getting Started with MicroPython on the Raspberry Pi Pico" book, which is a great read if you're a beginner!

import machine 
import utime
import gc

# Pico Display boilerplate
import picodisplay as display
width = display.get_width()
height = display.get_height()
gc.collect()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)

# reads from Pico's temp sensor and converts it into a more manageable number
sensor_temp = machine.ADC(4) 
conversion_factor = 3.3 / (65535)
temp_min = 10
temp_max = 30
bar_width = 5

# Set the display backlight to 50%
display.set_backlight(0.5)

temperatures = []

colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]


def temperature_to_color(temp):
    temp = min(temp, temp_max)
    temp = max(temp, temp_min)

    f_index = float(temp - temp_min) / float(temp_max - temp_min)
    f_index *= len(colors) - 1
    index = int(f_index)

    if index == len(colors) - 1:
        return colors[index]

    blend_b = f_index - index
    blend_a = 1.0 - blend_b

    a = colors[index]
    b = colors[index + 1]

    return [int((a[i] * blend_a) + (b[i] * blend_b)) for i in range(3)]


while True:
    # fills the screen with black
    display.set_pen(0, 0, 0)
    display.clear()

    # the following two lines do some maths to convert the number from the temp sensor into celsius
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721
    
    temperatures.append(temperature)

    # shifts the temperatures history to the left by one sample
    if len(temperatures) > width // bar_width:
        temperatures.pop(0)

    i = 0
    for t in temperatures:
        # chooses a pen colour based on the temperature
        display.set_pen(*temperature_to_color(t))
    
        # draws the reading as a tall, thin rectangle
        display.rectangle(i, height - (round(t) * 4), bar_width, height)

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width
    
    # heck lets also set the LED to match
    display.set_led(*temperature_to_color(temperature))

    # draws a white background for the text
    display.set_pen(255, 255, 255)
    display.rectangle(1, 1, 100, 25)
    
    # writes the reading as text in the white rectangle
    display.set_pen(0, 0, 0)
    display.text("{:.2f}".format(temperature) + "c", 3, 3, 0, 3)
    
    # time to update the display
    display.update()
    
    # waits for 5 seconds
    utime.sleep(5)
