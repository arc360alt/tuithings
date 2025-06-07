# ARKFETCH
## A highly customizable Neofetch like tool made in Python

# Installation
Windows: I personaly dont use windows anymore, so i do not know.
Linux:
- Download the Python File
- Install psutil and wmctrl via pip
- Install [Nerd Fonts](https://www.nerdfonts.com/) and set it as your terminal defualt
- Run the python file

# Configuration
## It is Very easy to configure this app, heres how!
#### Way #1:
- Changing the Python file to whatever you want it to be
#### Way #2 (RECCOMENDED):
- Creating a text file and instead of running ``python arkfetch.py`` you run ``python arkfetch.py yourfile.txt``
- Inside of that text file, you can put:

LINES:  |  TEXT:
````
1          Color of your ascii art
2          Color of the rest of the text
3          The text that shows up after running the script
4          The theme you want to use, EX: t1 or t2
5-end      Your ascii art
````
List of usable colors for lines 1-2:

Normal: black, red, green, yellow, blue, magenta. cyan , white

Bright:
Just add bright_ to any of the normal colors

bg colors:
Just add bg_ to any of the normal colors

You can see what colors they come out to in the python file.

# THEMES
- Use the argument -t1 for the original theme
- Use argument -t2 for the new theme that is basied off of [this](https://raw.githubusercontent.com/harilvfs/fastfetch/refs/heads/old-days/fastfetch/config.jsonc) FastFetch configuration
- Put t1 or t2 in line 4 of your config to choose the theme whithout having to spesify it in the command

EXAMPLE CONFIGURATION FOR MINT USERS:
```
green
white
i use mint btw
t2
             ...-:::::-...                 
          .-MMMMMMMMMMMMMMM-.             
      .-MMMM`..-:::::::-..`MMMM-.         
    .:MMMM.:MMMMMMMMMMMMMMM:.MMMM:.        
   -MMM-M---MMMMMMMMMMMMMMMMMMM.MMM-     
 `:MMM:MM`  :MMMM:....::-...-MMMM:MMM:`    
 :MMM:MMM`  :MM:`  ``    ``  `:MMM:MMM:    
.MMM.MMMM`  :MM.  -MM.  .MM-  `MMMM.MMM.   
:MMM:MMMM`  :MM.  -MM-  .MM:  `MMMM-MMM:   
:MMM:MMMM`  :MM.  -MM-  .MM:  `MMMM:MMM:   
:MMM:MMMM`  :MM.  -MM-  .MM:  `MMMM-MMM:   
.MMM.MMMM`  :MM:--:MM:--:MM:  `MMMM.MMM.   
 :MMM:MMM-  `-MMMMMMMMMMMM-`  -MMM-MMM:    
  :MMM:MMM:`                `:MMM:MMM:     
   .MMM.MMMM:--------------:MMMM.MMM.      
     '-MMMM.-MMMMMMMMMMMMMMM-.MMMM-'       
       '.-MMMM``--:::::--``MMMM-.'         
            '-MMMMMMMMMMMMM-'               
               ``-:::::-``
```

## Examples:
- Arch Linux
![image](https://github.com/user-attachments/assets/8ee3db3e-c855-4e00-a265-59b6671be1bf)
- New Theme using Nerd Fonts
![image](https://github.com/user-attachments/assets/08ad935d-9d13-4083-9253-09b466de4fc9)
