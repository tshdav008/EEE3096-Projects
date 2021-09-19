# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer =  33
eeprom = ES2EEPROMUtils.ES2EEPROM() 
count = 0
guessV = 0
fixVal = 0 
pi_pwm = None
pi_pwm_buzzer = None 
eeprom.write_byte(0, count) 
numOfGuess = 0
name = ""

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    if(count  ==  1):
        print("1 Empty") 
        print("2 Empty") 
        print("3 Empty")
    
    if(count == 1):
        print("1  " +raw_data[0][0]+ " took " + str(raw_data[0][1]) + " guesses") 
        print("2 Empty")
        print("3 Empty")
        
    elif(count == 2):
        print("1 " +raw_data[0][0]+ " took " + str(raw_data[0][1]) + " guesses") 
        print("2  " +raw_data[1][0]+ " took " + str(raw_data[1][1]) + " guesses") 
        print("3  Empty")
    elif(count >= 3):
        print("1  " +raw_data[0][0]+ " took " + str(raw_data[0][1]) + " guesses") 
        print("2  " +raw_data[1][0]+ " took " + str(raw_data[1][1]) + " guesses") 
        print("3  " +raw_data[2][0]+ " took " + str(raw_data[2][1]) + " guesses") 

# Setup Pins
def setup():
    # Setup board mode
    # Setup regular GPIO
    # Setup PWM channels
    # Setup debouncing and callbacks
    global pi_pwm
    global pi_pwm_buzzer
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_value[0],GPIO.OUT)
    GPIO.setup(LED_value[1],GPIO.OUT)
    GPIO.setup(LED_value[2],GPIO.OUT)
    GPIO.setup(LED_accuracy,GPIO.OUT) 
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    pi_pwm = GPIO.PWM(LED_accuracy,1000) 
    pi_pwm.start(0)
    pi_pwm_buzzer =  GPIO.PWM(buzzer,1000)
    GPIO.add_event_detect(btn_submit,GPIO.FALLING, callback = btn_guess_pressed, bouncetime = 500)
    GPIO.add_event_detect(btn_increase,GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 500)
    GPIO.output(buzzer,False) 
    GPIO.output(LED_value[0],False) 
    GPIO.output(LED_value[1],False) 
    GPIO.output(LED_value[2],False)

    
    
# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    # convert the codes back to ascii
    # return back the results
    score_count = eeprom.read_byte(0)
    scores = eeprom.read_block(1,score_count*4)
    arr = []
    arr2 = []
    i = 3
    num = score_count*4
while True:
    time.sleep(0.1)
    if i >= num:
        break
    else:
        str1 = chr(scores[i-3])+" "+chr(scores[i-2])+" "+chr(scores[i-1])
        gues = scores[i]
        i = i + 4
        arr.append(str1)
        arr.append(gues)
        
        for z in range(score_count):
            arr2.append([])
            index = 0
            x = 0
while True:
    if (x >score_count-1):
        break
    else:
        
        arr2[x].append(arr[index])
        arr2[x].append(arr[index+1])
        index = index + 2
        x = x + 1
        arr2.sort(key=lambda x: x[1])
        return score_count, arr2


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    global name
    global numOfGuess
    global pi_pwm
    global pi_pwm_buzzer
    count, data = fetch_scores()
    count = count + 1
    data.append([])
    name = name[0:3]
    data[count-1].append(name)
    data[count-1].append(numOfGuess)
    eeprom.write_byte(0, count)
    scores = data
    scores.sort(key=lambda x: x[1])
    data_to_write = []
    for score in scores:
        for letter in score[0]:
            data_to_write.append(ord(letter))
            data_to_write.append(score[1])
            eeprom.write_block(1, data_to_write)
            numOfGuess = 0


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    global count 
    global guessV 
    global pi_pwm
    pi_pwm.ChangeDutyCycle(0) 
    guessV=count 
    
    if(count==0):
        GPIO.output(LED_value[0],False) 
        GPIO.output(LED_value[1],False) 
        GPIO.output(LED_value[2],False)
    if(count==1): 
        GPIO.output(LED_value[0],True) 
        GPIO.output(LED_value[1],False) 
        GPIO.output(LED_value[2],False)
    if(count==2): 
        GPIO.output(LED_value[0],False) 
        GPIO.output(LED_value[1],True) 
        GPIO.output(LED_value[2],False)
    if(count==3):
        GPIO.output(LED_value[0],True) 
        GPIO.output(LED_value[1],True) 
        GPIO.output(LED_value[2],False)
    if(count==4): 
        GPIO.output(LED_value[0],False) 
        GPIO.output(LED_value[1],False) 
        GPIO.output(LED_value[2],True)
    if(count==5):
        GPIO.output(LED_value[0],True) 
        GPIO.output(LED_value[1],False) 
        GPIO.output(LED_value[2],True)
    if(count==6): 
        GPIO.output(LED_value[0],False) 
        GPIO.output(LED_value[1],True) 
        GPIO.output(LED_value[2],True)
    if(count==7): 
        GPIO.output(LED_value[0],True) 
        GPIO.output(LED_value[1],True) 
        GPIO.output(LED_value[2],True)
    count =  count  +  1
    if(count ==8):
        count =  0
    time.sleep(0.1)

# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global count
    global pi_pwm
    global numOfGuess
    count = 0
    numOfGuess = numOfGuess + 1
    start_time = time.time()
    while GPIO.input(channel) == 0:
        time.sleep(0.1)
    button_time = time.time() - start_time
    if .1<=button_time <=0.7:
        accuracy_leds()
   
    elif 0.7<button_time:
        pi_pwm = None 
    trigger_buzzer()
    pi_pwm_buzzer = None
    numOfGuess = 0
    name = ""
    GPIO.remove_event_detect(btn_submit)
    GPIO.remove_event_detect(btn_increase)
    GPIO.output(LED_value[0],False)
    GPIO.output(LED_value[1],False)
    GPIO.output(LED_value[2],False)
    GPIO.output(buzzer,False)
    GPIO.cleanup()
    setup()
    welcome()
    while True:
        time.sleep(0.1)
    menu()
    pass
    time.sleep(0.1)
       

# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global guessV 
    global fixVal 
    global pi_pwm
    dc = 0
    if(guessV <= fixVal):
        dc  =  (guessV/fixVal)*100
    else:
        dc  =  ((8-guessV)/(8-fixVal))*100
    pi_pwm.ChangeDutyCycle(dc) 
    time.sleep(0.1)

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global pi_pwm_buzzer
    global guessV
    global fixVal
    global name
    global pi_pwm
    absV = abs(fixVal-guessV)
    pi_pwm_buzzer.start(0)
    pi_pwm_buzzer.ChangeDutyCycle(0)
    start = time.time()
    if(absV==3):
        pi_pwm_buzzer.ChangeDutyCycle(50)
    while True:
        time.sleep(0.1)
    try:
        pi_pwm_buzzer.ChangeFrequency(1)
        time.sleep(0.1)
        stop = time.time()
    if(stop-start>5):
        stopAlertor()
        break
    except Exception as e:
        print("some error")
    if(absV==2):
        pi_pwm_buzzer.ChangeDutyCycle(50)
    while True:
        time.sleep(0.1)
    try:
        pi_pwm_buzzer.ChangeFrequency(2)
        time.sleep(0.1)
        stop = time.time()
    if(stop-start>5):
        stopAlertor()
        break
    except Exception as e:
        print("some error")
        
    if(absV==1):
        pi_pwm_buzzer.ChangeDutyCycle(50)
        
    while True:
        time.sleep(0.1)
    try:
        pi_pwm_buzzer.ChangeFrequency(4)
        time.sleep(0.1)
        stop = time.time()
    if(stop-start>5):
        stopAlertor()
        break
    except Exception as e:
        print("some error")
    if(absV == 0):
        print("Correct!!!!")
    name = input("Enter name with 3 or more characters:\n")
save_scores()
pi_pwm = None
pi_pwm_buzzer = None
numOfGuess = 0
name = ""
GPIO.remove_event_detect(btn_submit)
GPIO.remove_event_detect(btn_increase)
GPIO.output(LED_value[0],False)
GPIO.output(LED_value[1],False)
GPIO.output(LED_value[2],False)
GPIO.output(buzzer,False)
GPIO.cleanup()
setup()
welcome()
while True:
    time.sleep(0.1)
menu()
pass
stopAlertor()
time.sleep(0.1)
def startAlertor():
    pi_pwm_buzzer.start(50)
def stopAlertor():
    pi_pwm_buzzer.stop()

def main():
    try:
        setup()
welcome()
while True:
    time.sleep(0.1)
menu()
pass

except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print("some error")
print(e)
finally:
    GPIO.output(LED_value[0],False)
    GPIO.output(LED_value[1],False)
    GPIO.output(LED_value[2],False)
    GPIO.output(buzzer,False)
    pi_pwm.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    if __name__ == "__main__":
        main()