# List of Important Changes From Original Repo
* Added all changes from github.com/sean820117/auto-maple (TMS user) which adds a plethora of new features
* 09/06/2023: prevent elite boss stopping the bot
* ~sometime after new age patch: Updated rune logic to handle instanced maps and other players on map
* 12/10/2023: public mvp ping to discord (requires chat box to be on the bottom left, require .env file to be filled out in the repo, look at env_example file)
* 12/28/2023: purple portal ping to discord with spawn time (90s spawn)
   * frequency of portal should be every 4 * (10 mins + (1000 kills / ? kpm ))  = ~ 56-60 mins for 200-250 kpm
   * more info on portal https://strategywiki.org/wiki/MapleStory/Bounty_Hunt
* 1/3/2024: Added missing commits back from original repo (PR#150) from May - Jul, Dec 2022 
* Updated assets to support GMS instead, better handling of unexpected popups, more discord pings, removed unnecessary code
* 1/5/2024: Rune solve improvement - remove noise pt 1 (capture frame before clicking rune, capture frame after and filter out matching area)