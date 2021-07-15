def loop():
    try:
        while True:
            print(1)   # set dc value as the duty cycle
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        print(2)
        
loop()
    
