# Rune solver issue - Notes

## a. SPINNER ISSUE
* Current frame recording “s_timeframe” recordings spinners are exactly opposite in direction (if it went straight?) within 1 frame
* Using this , every 2 frames should be same arrow
    * ??? how can i use this
    * if 1 frame apart is not opposite direction then the spinner solution is somewhere between these two frames 
        * determine the angle of the arrow and find the closest 90th degree ? 
    * 




## b. PINK/PURPLE/BLUEORANGE ARROW ISSUE
* Green yellow colors are fine
* Blue puirple red are not fine 
fail folder = 1366x768 purple orange arrows, no spinner between  9/19 - 10/9 (hypothesis) there should be some that failed that are good on color 


* filter_color hsv removes purple/orange arrows - investigate

* get HSV values for all combination of arrows, allow those colors (OR) in the filter_color 
* multi mask

## c. Full screen issue (doesn't reach the right arrows?)
* Needs investigation

# Other Bot Issues
* Pressing up on pollo/frito/esp portal brings up dialogue, gets stuck
* Dying, gets stuck
* 