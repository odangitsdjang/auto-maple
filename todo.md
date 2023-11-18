# Rune solver issue - Notes

## a. SPINNER ISSUE
* Current frame recording “s_timeframe” recordings spinners are exactly opposite in direction (if it went straight?) within 1 frame
* Using this , every 2 frames should be same arrow
    * ??? how can i use this
    * if 1 frame apart is not opposite direction then the spinner solution is somewhere between these two frames 
        * determine the angle of the arrow and find the closest 90th degree ? 
    * 




## b. PINK/PURPLE/BLUEORANGE ARROW ISSUE
* Issue Reason: filter_color is only filtering hue from 1-75, which includes only red, orange, yellow, green
* Solution Proposal: Include more colors in filter_color but be more specific on Saturation and Value to maintain the noise 

fail folder = 1366x768 purple orange arrows, no spinner between  9/19 - 10/9 (hypothesis) there should be some that failed that are good on color 


* List of all colors and measured hsv value from game (pass/fail): h (0-180) s (0-255) v (0-255)
  - Red ():
  - Orange ():
  - Yellow ():
  - Green (p):
  - Blue ():
  - Purple ():

  h 0 - 180
  s 134 - 255
  v 199 - 255
  ( No green border)

  keep green border = 
  h 0 - 180
  s 175 - 255
  v 157 - 255

Test this value on images and see if it passes merge_detection function
Test more images

* Another option: use bitwise_or to create unified mask https://stackoverflow.com/questions/48109650/how-to-detect-two-different-colors-using-cv2-inrange-in-python-opencv 
  - get HSV values for all combination of arrows, allow those colors (OR) in the filter_color 

## c. Full screen issue (doesn't reach the right arrows?)
* Needs investigation

# Other Bot Issues
* Pressing up on pollo/frito/esp portal brings up dialogue, gets stuck
* Bot goes to pick up rune that spawned for another player on instanced  (while having rune buff active)
* Supporting upscaled 2k resolution (may need to add new MM_TL, MM_BR images and then do further testing)
* Dying, gets stuck