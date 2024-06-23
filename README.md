
## About

Whenever I turned off Cold Turkey for productive reasons, I noticed that i'd get distracted soon after and forget to turn it back on.

So I built this tool to:
1. Detect a `block` being turned off
2. Wait X amount of time
3. Turn it back on
4. Repeat whole process using task scheduler.

C# will schedule the tasks.

Python will do the detection, waiting and enabling.

## How to use

Head to -> build 

Edit:
- `ConfigColdTurkey.ini` Mainly:
    - Block name
    - How much time to wait
    - Cold Turkey DB path ()
        - If it's not already like that, find the Program Data `data-app.db` of Cold Turkey -> Paste it in
        - You might have to do some digging for this but look within C:/ProgramData
- `ConfigSchedule`. Mainly:
    - How often to check if it's enabled in TaskScheduler

# Compiling

I used Visual Studio 2022 to compile C#.
I used Nuitka to compile the Python.
- ```python -m nuitka --onefile auto_enabler.py --windows-console-mode=disable```
- It might get detected as a virus but ignore it.


Enjoy!