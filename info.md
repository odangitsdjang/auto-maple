# Currently this bot runs great on 1366x768 resolution only

## Rune logic in code
## rune is not active on the map 
  -> if rune time is greater than cd (automatically solved) and doesnt have rune cd/buff (not manually solved)
    -> check for rune on map 
## else if rune is active on the map 
  -> wait for solve rune to complete (bot.py)
    -> check for rune active on map
      -> set to rune not active 
    -> check for rune on buff bar
      -> set to rune not active
      -> set to rune solved now 