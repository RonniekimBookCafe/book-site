# CORE-01 Practice Code · Robot 2 Keyboard Driving, Experiment Keys, and Guide Mission

**Reader code for *Physical AI with RoboCo: Robot Structure and Python Control* (CORE-01)**

This folder holds the code that drives the book's practice robot, **Robot 2 (Book-CORE-01-SCRIPT)**, from a Python script. You can drive the robot with the keyboard, change the direction of its wheels, and open its screen to show a guide message. In Part 4 of the book you use the number keys to change the wheel motor settings and compare how the robot moves.

| Step | What to do | Section of this document |
| --- | --- | --- |
| 1 | Put the folder in RoboCo's Scripts folder | 3. Installation |
| 2 | Connect the start file to Robot 2's Microcontroller | 4. Connecting and Running |
| 3 | Drive with the keyboard while reading the robot screen and the console | 5–7 |
| 4 | (Part 4) Compare by changing values with the number keys, in the same start file | 9. Experiment Keys |
| 5 | (Part 5) Run the guide mission with key 5, in the same start file | 10. Guide Mission |

---

## 1. What This Folder Lets You Do

- Drive forward and backward, turn, rotate in place, and move diagonally with W/S/A/D/Z/C/Q/E.
- Open and fold the robot's screen with key 1. Opening it while stopped shows the guide message.
- Read the current state on the robot screen (Text Screen) and past events in the console LOG.
- Compare speed, steering order, and display behavior by changing the values at the top of the start file.
- Return to the starting state at any time with key 0 (Reset All). When in doubt, press 0.
- In Part 4, change the wheel motor settings with number keys 2/3/4 and compare, all in the same start file and without opening the code.
- In Part 5, run the guide mission: the robot drives a set route on its own, guides, and comes back.

## 2. What You Need

| Item | Details |
| --- | --- |
| Game | RoboCo on Steam |
| Robot file | Book-CORE-01-SCRIPT (Robot 2, provided with the book) |
| This folder | Book_C01_Robot |

Robot 1 (Book-CORE-01-CONTROLS) is driven through Controls Mapping with no script, so it does not use this code.

## 3. Installation: Where the Folder Goes

Put the `Book_C01_Robot` folder **directly inside** RoboCo's **Scripts folder**.

```text
Documents
└─ My Games
   └─ RoboCo
      └─ [your Steam user name]
         └─ Scripts
            └─ Book_C01_Robot          ← this folder
               ├─ README.md
               ├─ __init__.py
               ├─ c01_start.py
               └─ C01_Lib
                  ├─ __init__.py
                  └─ c01lib_*.py (11 files)
```

In RoboCo, open the Microcontroller settings and click **OPEN SCRIPT FOLDER** to go straight to the Scripts folder.

Follow three rules when installing.

1. **Put it directly inside Scripts.** RoboCo looks for files starting from the Scripts folder. If you go one level deeper, as in `Scripts\OtherFolder\Book_C01_Robot`, the script cannot find its library.
2. **Don't rename the folders or files.** The start file loads the library by the names `Book_C01_Robot` and `C01_Lib`.
3. **When you get a new version, delete the old folder first.** If you copy over it, files that existed only in the old version stay behind and clutter the script list.

## 4. Connecting and Running

1. In RoboCo, load the robot file **Book-CORE-01-SCRIPT**.
2. Open the robot's **Microcontroller** settings and click **LOAD**.
3. Choose **c01_start.py** in the `Book_C01_Robot` folder.
4. When it runs, the following lines appear in the console. Once you see the `START` line, it's ready. If the robot file's motor settings differ from the values in the start file, one more line, `Motor (script)`, shows the values the script applied.

```text
[   0.00s] START   Ready - wheels 0°, screen folded, motors stopped
[   0.00s] KEYS    W forward · S back · A turn left · D turn right · Z rotate left · C rotate right · Q diag left · E diag right · 1 screen (fold = reset) · 0 reset
[   0.00s] KEYS    Experiment (PART 4): 2 next value · 3 level down · 4 level up | Mission (PART 5): 5 start
[   0.00s] SETUP   Steering wait 0.50s · stagger 0.30s · return 0.60s
[   0.00s] SETUP   Motor (robot file) RPM 120 rpm / ACCEL 0.50 s / BRAKE F 50.0 / BRAKE T 0.20 s
[   0.00s] SETUP   Motor (fixed)      TORQUE 6290 - not changed by the script
```

You connect **only one file, the start file `c01_start.py`**, to the robot, and you use it from Part 1 through Part 5 of the book. The Part 4 experiments use number keys 2/3/4 and the Part 5 guide mission uses key 5, all in this same file. The files in the `C01_Lib` folder are a library the script loads, so don't connect them to the robot directly.

## 5. Keys

| Key | Action | Wheel direction |
| --- | --- | --- |
| W | Forward | All four wheels at 0° |
| S | Backward | All four wheels at 0° |
| A | Turn left | All four wheels at 0°; left and right sides spin in opposite directions |
| D | Turn right | All four wheels at 0°; left and right sides spin in opposite directions |
| Z | Rotate left in place | Each wheel steers to 45°, then rotates |
| C | Rotate right in place | Each wheel steers to 45°, then rotates |
| Q | Diagonal forward-left | All four wheels point to 10 o'clock |
| E | Diagonal forward-right | All four wheels point to 2 o'clock |
| 1 | Open / fold the screen. **Folding does the same Reset All as 0** (Section 9) | — |
| 0 | **Reset All.** When in doubt, press 0 | Wheels stop and return to 0° |
| 2 · 3 · 4 | Part 4 experiment keys (Next Parameter · Level Down · Level Up). Opens the screen if it is folded (Section 9) | — |
| 5 | Start the guide mission (Start Mission) (Section 10) | Drives the route on its own |

All eight drive keys spin the wheels at the same Target RPM (`TARGET_RPM`). What differs between keys is not the speed but the wheel direction (steering angle) and which way each wheel turns (forward or backward).

The key assignments are listed in the start file's **2. KEYS** section (line 55). If you change a key there, set the same key in the robot file's Controls Mapping too.

Keys that need the wheels to change direction (Z/C/Q/E, and W/S/A/D right after using one of them) move in this order:

```text
Key pressed  : steer the front wheels → (0.3 s) → steer the rear wheels → (0.5 s) → drive the wheels
Key released : stop driving + ease all four wheels back to 0° over 0.6 s
```

The short pause while steering is not a malfunction. It's the robot waiting so the body doesn't twist while the wheels change direction.

## 6. Reading the Robot Screen (Text Screen)

The robot screen shows **the state at this very moment** in four lines.

```text
FORWARD      ← current action
KEY W        ← key the script read
RPM 120      ← Target RPM of the wheel motors
READY        ← steering state
```

| Line | Shows | Meaning |
| --- | --- | --- |
| 1 | STOP · FORWARD · BACKWARD · TURN L · TURN R · ROTATE L · ROTATE R · DIAG L · DIAG R | Current action |
| 2 | KEY W … KEY E, KEY - | Key the script read (- means no key pressed) |
| 3 | RPM 0 – 1000 | Target RPM set on the wheel motors. It's the target, not a measured speed, and reads 0 while steering or stopped |
| 4 | READY / STEERING | Whether steering is done (READY) or the wheels are changing direction (STEERING) |

Sometimes the screen shows one of these instead of the status:

- **Guide message**: Open the screen with key 1 while stopped and the text in `GUIDE_MESSAGE` appears (`WELCOME` by default). Pressing a drive key switches back to the status, which stays until you open the screen again. If you open it while driving, it keeps showing the status you need for driving.
- **RESET / KEY 0 / RPM 0 / READY**: Right after Reset All with key 0. Pressing a drive key brings the status back.
- **Experiment screen** (e.g. `RPM / LV 4/10 / 120 rpm / READY`): While stopped in Part 4 experiment mode. Even if the screen is folded, pressing 2/3/4 opens it automatically (Section 9).
- **Mission screen** (e.g. `MOVE / STEP 2/3 / ROTATE R / READY`): Shows the current state and step during the guide mission (Section 10).
- **ERROR / STOPPED / SEE LOG**: The script stopped because of an error. The wheel motors have already stopped. Check the `ERROR` line in the console.

## 7. Reading the Console LOG

The console records **what happened and when**, one line per event. The robot screen shows the current state, so the console only records events that change it. The LOG is written in **English** so it matches the robot screen, the key names, and the RoboCo API.

```text
[  20.00s] STEER   Pivot posture (front → rear stagger)
 ────┬────  ──┬──   ───────────────┬───────────────
 time since  category             message
 start
```

| Category | Meaning | Events recorded |
| --- | --- | --- |
| `START` | Start | The script is ready |
| `KEYS` | Key guide | Keys you can use |
| `SETUP` | Settings | This run's steering timing and motor settings (robot file values, values the script applied, fixed values) |
| `STEER` | Steering | The wheel posture changes (normal driving, rotate in place, diagonal) |
| `SCREEN` | Screen | Key 1 opens or folds the screen |
| `DRIVE` | Driving | One-line summary when a drive key is released (only at `LOG_LEVEL` 2) |
| `EXP` | Experiment | Experiment mode, value changes, RESET, ignored keys |
| `STATE` | Mission state | Guide mission state changes and route steps (WAIT → MOVE, etc.) |
| `END` | End | The script ended |
| `ERROR` | Error | An error while running |
| `NOTE` | Notice | LOG line limit reached, guide message too long, motor setting out of range, unused value name |

Common words: `step` a route step, `route` the route, `mission complete`, `forward`, `back`/`backward`, `turn`, `rotate` rotate in place, `diagonal`, `posture` wheel posture, `stagger` staggered timing, `return` return to 0°, `base` baseline, `level (LV)`, `held` how long the key was held, `rpm` Target RPM, `fixed` fixed value, `ignored` not accepted.

`LOG_LEVEL` sets how much is recorded.

| LOG_LEVEL | What is recorded | When to use it |
| --- | --- | --- |
| 0 | START · KEYS · SETUP · END · ERROR · RESET | You rarely look at the console |
| 1 (default) | 0 + wheel posture changes, screen changes, experiment values, mission state | Everyday practice |
| 2 | 1 + one line per driving action (`W forward \| held 0.32s \| rpm 120`) | Experiments that compare values |

The `SETUP` lines record the steering timing and motor settings used in this run. When you experiment with values, keep these lines with your notes so you always know which settings produced which result.

## 8. Values to Try Changing First

The start file `c01_start.py` only holds the values you can change and the key assignments. The code that moves the robot lives in the library in the `C01_Lib` folder (Section 11). The "setup code" at the very top makes sure the library loads correctly, so leave it alone.

| Section | Line | What it holds | Used in |
| --- | --- | --- | --- |
| 1. CONTROL PARAMETERS | 32 | Wheel motor settings, steering timing, guide message, console log detail | Every part |
| 2. KEYS | 55 | Key assignments (drive keys, command keys) | Every part |
| 3. EXPERIMENT STEPS | 79 | Experiment level table (LV 1–10 values for each item) | Part 4 (Section 9) |
| 4. MISSION | 94 | Guide mission route and timing | Part 5 (Section 10) |
| 5. RUN | 109 | Three lines that set up once and repeat until stopped | Every part |

The values in **1. CONTROL PARAMETERS**:

| Value | Default | Meaning | When to change it |
| --- | --- | --- | --- |
| `TARGET_RPM` | 120 | Target wheel speed (Target RPM, 0–1000). Wheel speed for all eight drive keys | Lower it if the robot is too fast. Baseline for the Part 4 experiments |
| `ACCELERATION_TIME` | 0.5 | Time to reach Target RPM when starting (s, 0–10) | Raise it if the body jolts when starting. Baseline for the Part 4 experiments |
| `MAX_BRAKE_FORCE` | 50 | Braking force when stopping (Max Brake Force, 0–1570) | Baseline for the Part 4 experiments |
| `BRAKING_TIME` | 0.2 | Time the brake takes to stop the wheels (s, 0–10) | Baseline for the Part 4 experiments |
| `STEERING_SETTLE_SEC` | 0.5 | Wait after steering before the wheels drive (s) | At 0, steering and driving start together |
| `STEERING_STAGGER_SEC` | 0.3 | Delay between steering the front and rear wheels (s) | At 0, all four wheels steer at once |
| `RELEASE_RETURN_SEC` | 0.6 | Time to return the wheels to 0° on key release (s) | Raise it if the body jolts on the return |
| `GUIDE_MESSAGE` | "WELCOME" | Guide message (up to 9 characters per line and 4 lines; `\n` breaks a line) | e.g. "EXIT\nTHIS WAY" |
| `LOG_LEVEL` | 1 | Console log detail (0/1/2) | See the table in Section 7 |

**The four wheel motor settings use the same names and ranges as RoboCo's settings panel (DC Motor).** They're applied to all four wheels when the script starts. A value outside its range is set to the nearest end of the range, and a `NOTE` line appears in the console (e.g. `TARGET_RPM = 1200` → 1000). The other two items in the settings panel aren't changed by the script: **Max Torque** (6290) is fixed, and **Start On** (ON) has no matching Python API property. The Max Torque value is recorded in the console's `SETUP  Motor (fixed)` line at startup.

**More values you can change.** These are changed less often, so they aren't written in the start file. To change one, add a line with the same name in section 1, such as `LOG_MAX_LINES = 500`.

| Value | Default | Meaning |
| --- | --- | --- |
| `STEERING_STAGGER_ORDER` | "front_rear" | Staggered steering order. "diagonal" steers diagonal pairs first |
| `STAGGER_ON_RELEASE` | False | Whether to stagger the steering on key release too (used only when `RELEASE_RETURN_SEC` is 0) |
| `LOOP_DELAY_SEC` | 0.02 | How often key input is checked (s). Usually left as is |
| `LOG_MAX_LINES` | 200 | Maximum number of console log lines |
| `TEXT_SCREEN_FONT_SIZE` | None | Robot screen font size. If text gets cut off, set a smaller number (e.g. 40) |

If you misspell a value's name (e.g. `LOG_LEVL`), that value isn't used, and a `NOTE  Unknown setting 'LOG_LEVL'` line appears in the console at startup.

Follow this order when you change values:

1. Change **only one value at a time.** If you change several together, you can't tell which one changed the result.
2. Write down the value before you change it. The defaults in the table above are the original values provided.
3. Run again from the same starting position and compare the results.

## 9. Changing Values with the Experiment Keys (Part 4)

The Part 4 experiments in the book use the number keys in **the same start file** (`c01_start.py`). You can change the wheel motor settings and compare the motion using only the keys, without opening the code.

| Key | Name | What it does | Accepted when |
| --- | --- | --- | --- |
| 2 | Next Parameter | The first press **starts experiment mode** (RPM). After that, it picks the next value (RPM → ACCEL → BRAKE F → BRAKE T → RPM again). Values changed with 3/4 stay as they are | Stopped |
| 3 / 4 | Level Down / Level Up | Lowers or raises the chosen value one level. Applied to the robot the moment you press it | Experiment mode + stopped |
| 0 | Reset All | **Resets everything.** Every value changed with 3/4 back to baseline, wheels stopped, wheels at 0°, experiment mode ended | Any time |
| 1 (when folding) | Toggle Screen | Folding the screen does **the same Reset All as 0** | When no mission is running |

- **Experiment mode starts the first time you press 2.** Until then the screen and LOG work as usual, and pressing 3 or 4 changes nothing (the console gets one line telling you to press 2 first).
- **Stopped** means no drive key is held and the fourth line of the robot screen reads `READY`. Pressing 2/3/4 while driving, or while the wheels are changing direction (`STEERING`), changes nothing.
- **Pressing 2/3/4 opens the screen.** The experiment results appear on the robot screen, so if the screen is folded it opens on its own and shows the experiment screen. If you opened the screen with key 1 and the guide message is showing, pressing 2 switches to the experiment screen. When a key is not accepted (while driving, or 3/4 before experiment mode), the screen doesn't move either.
- **A value changed with 3/4 stays when you pick another value with 2.** For example, raise RPM to 300 and then pick ACCEL with 2: RPM stays at 300 while you change ACCEL. You can drive with several values changed at once, and the console's `Next:` line ends with the kept value, like `RPM kept at 300 rpm`.
- **To return the changed values to their baselines, press 0 or fold the screen with 1.** Both do the same Reset All. A drive key you were holding at that moment must be released and pressed again to move. Folding the screen with 1 while driving also stops the wheels.

While stopped in experiment mode, the robot screen shows the experiment screen. Pressing a drive key switches to the status screen from Section 6.

```text
RPM          ← chosen value (changed with key 2)
LV 4/10      ← current level
120 rpm      ← current value
READY        ← steering state (READY / STEERING)
```

There are four values you can experiment with, and key 2 picks them in this order. Each has 10 levels, and **the value in bold is the baseline (the CONTROL PARAMETERS value from Section 8)**. LV 10 is the maximum in RoboCo's settings panel, so key 4 can take a value all the way to its maximum.

| Order | Screen name | Value changed (where the baseline lives) | LV 1 – LV 10 | Base level |
| --- | --- | --- | --- | --- |
| 1 | RPM | Target wheel speed (`TARGET_RPM`) | 30 · 60 · 90 · **120** · 200 · 300 · 400 · 600 · 800 · 1000 | LV 4 |
| 2 | ACCEL | Acceleration time from a stop (`ACCELERATION_TIME`, s) | 0.1 · 0.2 · **0.5** · 1 · 2 · 3 · 4 · 6 · 8 · 10 | LV 3 |
| 3 | BRAKE F | Braking force (`MAX_BRAKE_FORCE`) | 0 · 25 · **50** · 100 · 200 · 400 · 600 · 900 · 1200 · 1570 | LV 3 |
| 4 | BRAKE T | Braking time (`BRAKING_TIME`, s) | 0 · 0.1 · **0.2** · 0.5 · 1 · 2 · 4 · 6 · 8 · 10 | LV 3 |

The levels are written out as values in the **3. EXPERIMENT STEPS section of `c01_start.py` (line 79)**. To change the levels, edit the values in the list, smallest first.

- **Each baseline lives only in CONTROL PARAMETERS.** If no level in the table equals the baseline, the nearest level is replaced with the baseline and a `NOTE` line appears in the console. For example, changing `TARGET_RPM` to 150 makes RPM's LV 4 150 instead of 120.
- A level outside the settings panel's range is set to the nearest end of the range, with a `NOTE` line.
- To experiment with the steering timing too, add a `("STAGGER", [...])` (`STEERING_STAGGER_SEC`) or `("RETURN", [...])` (`RELEASE_RETURN_SEC`) line to the table. Values are in seconds.

Two things to keep in mind:

- **When the script starts, the motor settings in CONTROL PARAMETERS are applied to the robot.** The values in RoboCo's settings panel change to match. That way every experiment starts from the same conditions. At startup, the console's `SETUP  Motor (robot file)` line records the robot file's values from before the script changed them.
- **When the script stops (including on an error), the values go back to their baselines.** If the script can't run its wrap-up code, for example because you closed the game right away, the changed values may stay on the robot. If the robot moves differently than usual, start the script again and press 0, or reload the robot file.

Each value change writes an `EXP` line to the console. You can use these lines as your experiment record as is.

```text
[   2.70s] EXP     Target RPM 120 rpm → 200 rpm (LV 4 → 5)
[   3.40s] EXP     Next: ACCEL (Acceleration Time) LV 3/10 0.50 s | RPM kept at 200 rpm
[   9.10s] EXP     RESET (key 1 - screen folded) - all values to base, wheels stopped and back to 0°. Release drive keys, then press again
```

## 10. Guide Mission (Part 5)

In Part 5 of the book, you run the guide mission with key 5 in **the same start file** (`c01_start.py`). Press 5 and the robot drives a set route on its own to the guide point, opens its screen to show the guide message, and retraces the route back to where it started.

| Key | Name | What it does |
| --- | --- | --- |
| 5 | Start Mission | Starts the mission. Accepted only while the robot is stopped and the fourth line of the screen reads `READY` |
| 0 | Reset All | **Stops the mission and resets everything.** Stops the wheels, folds the screen, and returns to WAIT. When in doubt, press 0 |

The mission passes through four states in order. The current state appears on the first line of the robot screen and in the console's `STATE` lines.

```text
WAIT ──key 5──▶ MOVE ──end of route──▶ GUIDE ──guide time over──▶ RETURN ──▶ WAIT
                  │                       │                          │
                  └────────────── key 0: back to WAIT at any time ───┘
```

| State | What the robot does | Robot screen |
| --- | --- | --- |
| WAIT | You can drive with the keys as usual. Press 5 to start the mission | Normal status screen (`STOP / KEY - / …`) |
| MOVE | Runs the actions in `MISSION_ROUTE` in order | `MOVE / STEP 2/3 / ROTATE R / READY` |
| GUIDE | Stops, opens the screen, and shows the guide message | The guide message (e.g. `WELCOME`) |
| RETURN | Retraces the same route in reverse | `RETURN / STEP 1/3 / BACKWARD / READY` |

**The values to try changing** are in the start file's **4. MISSION section (line 94)**. The guide message comes from `GUIDE_MESSAGE` in section 1.

| Value | Default | Meaning |
| --- | --- | --- |
| `MISSION_ROUTE` | Forward 2 s → rotate right in place 0.5 s (about 90°) → forward 1.5 s | The route from the start point to the guide point, written as `(action, seconds)` pairs in order |
| `GUIDE_SEC` | 3.0 | How long the screen stays open to guide (s) |
| `STEP_PAUSE_SEC` | 0.5 | Pause between one action and the next (s) |
| `RETURN_TO_START` | True | True: return to the start point after guiding. False: end at the guide point |

The actions you can use in a route are `forward`, `backward`, `turn_left`/`turn_right` (turn), `rotate_left`/`rotate_right` (rotate in place), and `pause` (stop and wait). An unknown action or an action with a time of 0 is skipped, and a `NOTE` line is written to the console.

**Start position and route.** A route isn't a set of map coordinates; it's **a series of actions relative to where the robot is standing**. Whether you start in the middle of the sandbox or at another starting point, the robot runs the same route from wherever it sits. Before starting the mission, check that the robot is facing the way you want it to go. On the way back, the route runs in reverse order with each action swapped for its opposite (forward ↔ backward, left ↔ right), so the robot returns to its start point while keeping the same heading.

Five things to keep in mind:

- **This robot moves by time.** It has no sensor that measures position, so a finished action means "moved for the set time," not "arrived at the target point." On a slippery floor or if the body gets pushed, the robot drifts a little, and where it ends up may differ slightly from where it started. Drive time is measured from the moment the wheels actually start rolling (time spent changing wheel direction isn't counted).
- **Turn angles are set by time too.** The default route's `("rotate_right", 0.5)` is the time that turns about 90° at the baseline values (Target RPM 120, Acceleration Time 0.5 s). The wheels spend the first 0.5 s speeding up, so the angle isn't proportional to the time, which is why going from 180° to 90° didn't simply halve the time. If the angle is off on your floor or robot, adjust it 0.05 s at a time (shorter if it turns too far, longer if it falls short).
- **The mission uses the driving settings in section 1 as is.** Change a wheel motor setting or the steering timing and the mission's motion changes too. If you press 5 while experiment mode has a value changed, every value is restored to its baseline before the robot sets off (the console shows an `EXP  Experiment mode off …` line).
- **During the mission, drive keys, key 1, and keys 2/3/4 are ignored.** This keeps key presses from disturbing a running mission. Each key you press is noted in the console, like `STATE  Key W ignored - mission is running`. Press 0 to stop.
- **Routes have no diagonal (Q/E) actions,** because there is no "diagonal backward" action to use on the way back. Use rotate in place to change direction.

The console writes one line for each state and step. When the mission ends, the elapsed time is recorded too, so you can compare runs before and after you change the route.

```text
[   0.50s] STATE   WAIT → MOVE - 3 steps
[   0.50s] STATE   MOVE step 1/3: forward 2.00s
[   8.36s] STATE   MOVE → GUIDE - showing guide 3.0s
[  11.36s] STATE   GUIDE → RETURN - same route in reverse
[  19.24s] STATE   RETURN → WAIT - mission complete (18.7s)
```

## 11. Files and Control Flow

| File | Role |
| --- | --- |
| `c01_start.py` | **Start file.** Values to change, key assignments, experiment level table, mission route, and the three "set up → repeat" lines |
| `C01_Lib/c01lib_app.py` | Sets up the robot from the start file's values and, in the main loop, reads the keys and runs driving, experiments, and the mission |
| `C01_Lib/c01lib_keys.py` | Key input: drive keys (while held, most recent key wins) and command keys (once, on press) |
| `C01_Lib/c01lib_robot.py` | The `Robot` class for the whole robot. Steering → drive order, screen and LOG display |
| `C01_Lib/c01lib_drive.py` | Controls the four wheel DC motors as one group |
| `C01_Lib/c01lib_steering.py` | Controls the four steering servos as one group (angles per posture, staggered steering) |
| `C01_Lib/c01lib_screen.py` | Controls the servo that opens and folds the screen |
| `C01_Lib/c01lib_led.py` | Color of the input LED |
| `C01_Lib/c01lib_log.py` | Console LOG format and detail level |
| `C01_Lib/c01lib_experiment.py` | Part 4 experiments: experiment mode, applying values, automatic restore, RESET, experiment screen |
| `C01_Lib/c01lib_mission.py` | Part 5 guide mission: state flow (`Mission`), running the route (`RouteRunner`), the return route |
| `C01_Lib/c01lib_ports.py` | **Hardware map.** Port for each part, motor direction, steering sign, screen angles |

Start from the start file, and when a topic catches your interest, open the matching library file.

| What you want to know | File to open |
| --- | --- |
| The set-up-once, repeat-forever structure | Section 5. RUN of `c01_start.py`, `c01lib_app.py` |
| How key presses and releases are read; most recent key wins | `c01lib_keys.py` |
| How the four wheel motors run as one group | `c01lib_drive.py` |
| Wheel direction, screen angles, and angle limits | `c01lib_steering.py`, `c01lib_screen.py`, `c01lib_ports.py` |
| The steer → wait → drive order | `c01lib_robot.py` |
| Console logging and the robot screen display | `c01lib_log.py`, `c01lib_robot.py` |
| How the experiment keys change values | `c01lib_experiment.py` |
| The mission's state flow and route execution | `c01lib_mission.py` |

When you press a key, the command travels in this order:

```text
Key input (W)
 → c01_start.py              app.update() repeats
 → c01lib_app.py / c01lib_keys.py   reads the key and calls robot.forward()
 → c01lib_robot.py            checks the steering posture; steers first if needed, then drives
 → c01lib_steering.py / c01lib_drive.py
 → RoboCo Python API          ServoMotor.spin_to_degrees(), DCMotor.spin()
 → Ports 1–8                  the actual servos and motors
 → robot motion
```

The book keeps the **official RoboCo API** separate from **the author's Educational Library**. In this code, functions such as `robot.forward()` belong to the author's library, not the official API.

| Kind | Examples | Where it lives |
| --- | --- | --- |
| Official RoboCo API | `DCMotor.spin(power)`, `DCMotor.stop()`, `ServoMotor.spin_to_degrees(angle)`, `ServoMotor.limits_degrees`, `LED.color`, `TextScreen.text`, `Input.stream(key)`, `Runtime.quitting()`, `DCMotor.max_rpm`·`acceleration_time`·`brake_force`·`brake_time`, `DCMotor.max_torque` (read only) | Built into RoboCo (the Microcontroller's **API** button) |
| Author's Educational Library | `Robot.forward()`, `Robot.rotate_left()`, `Robot.toggle_screen()`, `DriveMotors.all_forward()`, `SteeringServos.begin_posture()`, `DriveKeys.update()`, `Experiment.step()`, `Mission.update()`, `reverse_route()`, `log()` | `C01_Lib` in this folder |

**The "setup code" at the top of the start file** does two things:

- **It reloads the library.** When you run a script again, RoboCo doesn't restart Python from scratch; it remembers the library it loaded before. That means edits to the files in `C01_Lib` would be ignored and the old code would keep running. The setup code clears what RoboCo remembered and reloads the library on every run. It doesn't delete any files.
- **It doesn't create temporary files.** Python normally writes temporary files to a folder named `__pycache__`. Since the library is reloaded every time, those files aren't needed, so they're never created and your folder stays clean.

## 12. Robot Parts and Ports

There are several parts of the same kind, so the code sets the Port number for each part explicitly.

| Port | Part | Port | Part |
| --- | --- | --- | --- |
| 0 | Input LED | 6 | RR-Steering Servo |
| 1 | FR-DC Motor | 7 | RL-Steering Servo |
| 2 | RR-DC Motor | 8 | FL-Steering Servo |
| 3 | RL-DC Motor | 9 | Screen-Fold Servo |
| 4 | FL-DC Motor | 10 | Text Screen |
| 5 | FR-Steering Servo | | |

FL is front left, FR front right, RL rear left, and RR rear right, as seen from the direction the robot faces, not from the person looking at the screen.

## 13. When the Wheels or Screen Move the Wrong Way

If you rebuilt the robot yourself or a part faces a different way, check the following values in `C01_Lib/c01lib_ports.py`. Make direction fixes only in this file; don't change the key assignments.

| Symptom | Value to check |
| --- | --- |
| Pressing W spins the robot in place | Motor direction such as `FLIP_FL_DRIVE`, `FLIP_RL_DRIVE` (on the provided robot, the two left wheels are True) |
| Pressing Q points the wheels to 2 o'clock | Steering sign such as `STEERING_SIGN_FL` (on the provided robot, all four are -1) |
| Pressing key 1 moves the screen into the body | `SCREEN_DEPLOYED_DEG` (-90 on the provided robot) |

Change one axis at a time and run again to check. Flipping the same axis in two places puts it right back where it started.

## 14. Troubleshooting

| Symptom | Check | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'Book_C01_Robot'` in the console | Folder location and name | Put `Book_C01_Robot` directly inside Scripts and don't rename it (Section 3) |
| Unfamiliar files appear in the script list | Files left over from an old version | Delete the folder and put the new one in |
| No `START` line in the console after running | Script connection | LOAD the start file again following Section 4 |
| Nothing moves when you press a key | The robot file you loaded | Make sure it's Robot 2 (Book-CORE-01-SCRIPT). Robot 1 doesn't use a script |
| Z/C/Q/E pause briefly before moving | The fourth line of the screen | STEERING is normal. The wheels don't spin while steering |
| The body jolts when starting or rotating | The values in Section 8 | Raise `ACCELERATION_TIME` or lower `TARGET_RPM`. If it jolts on key release, raise `RELEASE_RETURN_SEC` |
| Text on the robot screen is cut off | Font size and message length | Set `TEXT_SCREEN_FONT_SIZE` to a smaller number. Keep the guide message within 9 characters per line and 4 lines |
| The guide message doesn't appear | The robot's state when the screen opened | Open the screen with key 1 while stopped. If you pressed a drive key, fold it and open it again |
| Korean text in the guide message doesn't show | The screen font | Write the message in English |
| The console log stops growing | The last `NOTE` line | `LOG_MAX_LINES` has been reached. Raise it or lower `LOG_LEVEL` |
| ERROR / STOPPED / SEE LOG on the robot screen | The console's `ERROR` line and the Python message below it | Check the file and line in the message, fix it, and run again |
| Pressing 2/3/4 changes nothing and the screen doesn't open | The console's `EXP` lines | For 3/4, press 2 first to start experiment mode. Release the drive keys and press once the fourth line of the screen reads READY |
| The robot moves strangely or you can't remember what you changed | — | Press 0 to reset everything |
| Folding the screen with 1 stopped the wheels and put the experiment values back | The console's `EXP  RESET (key 1 - screen folded)` line | That's normal. Folding the screen does the same Reset All as 0 (Section 9) |
| After an experiment, the robot moves differently from usual when restarted | The console's `SETUP  Motor (robot file)` line | Start the script, press 0, then stop it, or reload the robot file (Section 9) |
| Pressing 5 doesn't start the mission | The console's `STATE`/`NOTE` lines | Release the drive keys and press it while the screen reads READY. The mission won't start if `MISSION_ROUTE` is empty |
| Keys don't respond during the mission | The console's `STATE  Key … ignored` line | That's normal. Drive keys, 1, 2, 3, and 4 are ignored during the mission. Press 0 to stop |
| You changed a value in the start file but nothing changed | The console's `NOTE  Unknown setting` line | Check the spelling of the value's name (Section 8) |
| `NOTE  'MOTOR_POWER_RATIO' is no longer used …` in the console | Whether you're still using the 1.6.0 start file | Switch to the 1.6.3 start file or delete that line. Speed is set with `TARGET_RPM` (Section 15) |
| `NOTE  … is outside … is used` in the console | The range of the wheel motor settings | Set the value inside the range in the Section 8 table |
| In the mission the robot overshoots or stops short of the target | The times in `MISSION_ROUTE` | Adjust the time of one action at a time, a little at a time, and run again (Section 10) |
| After the mission the robot stops a little away from where it started | — | That's the error of a robot that moves by time. Reload the robot file and start again from the start position (Section 10) |
| You edited the library but nothing changed | Whether you ran it again | Stop the script and run it again. The library is reloaded on every run |

## 15. Version

This folder's release version is **1.6.3**. The same number appears at the top of every code file.

**Changes in 1.6.3 (from 1.6.2)**

- The rotate-in-place step of the guide mission (key 5) route is shortened from 0.8 s to 0.5 s. Since 1.6.1, Z/C rotation also runs at Target RPM, so 0.8 s turned about 180°; 0.5 s turns about 90°. The left turn on the way back uses the same 0.5 s.

**Changes in 1.6.2 (from 1.6.1)**

- The maximum of `TARGET_RPM` is corrected to 1000 (the range in RoboCo's settings panel).
- The experiment items are now the four wheel motor settings. Key 2 picks them in the order RPM → ACCEL → BRAKE F → BRAKE T. STAGGER and RETURN are no longer in the default table; add a line to the table to use them again.
- Experiments now have 10 levels instead of 5. The table lists the LV 1–10 values themselves instead of multipliers, and LV 10 is the maximum in the settings panel, so key 4 can go all the way up to the maximum.
- A value changed with 3/4 stays when you pick another value with 2. To return to the baselines, press 0 or fold the screen with 1.
- Folding the screen with key 1 does the same Reset All as key 0.

**Changes in 1.6.1 (from 1.6.0)**

- The wheel motor settings now use the same names, defaults, and ranges as RoboCo's settings panel (DC Motor): `TARGET_RPM` 120 (0–10000), `ACCELERATION_TIME` 0.5 (0–10), `MAX_BRAKE_FORCE` 50 (0–1570), `BRAKING_TIME` 0.2 (0–10). A value outside its range is set to the nearest end of the range.
- `MAX_TORQUE` has been removed. Max Torque is fixed at 6290, so the script doesn't change it; it's only recorded in the `SETUP  Motor (fixed)` line at startup. The `TORQUE` experiment item has been removed too.
- `MOTOR_POWER_RATIO`, `TURN_POWER_RATIO`, and `PIVOT_POWER_RATIO` have been removed. Wheel speed is set by `TARGET_RPM` alone, and all eight drive keys spin the wheels at the same Target RPM. The `POWER` experiment item has been removed too (8 experiment items → 6).
- The third line of the robot screen and the `DRIVE` line show the Target RPM (`RPM 120`, `rpm 120`) instead of the power ratio (`PWR 1.00`, `power 1.00`).
- If a name from the 1.6.0 start file is still there, that value isn't used, and a `NOTE` line in the console says why.

This code was checked on the RoboCo version listed in the book's "What You Need to Follow This Book." If a RoboCo update changes how things work, check the book's companion page for the latest release and errata. When you get a new version, delete the old folder first and then put the new one in, following the rules in Section 3.

## 16. Good to Know

RoboCo is a game made by Filament Games. This code is not an official RoboCo example or official course material; the author wrote it for the exercises in this book. Use and redistribution follow the copyright notice in the book.

*This is the English-comment edition of release 1.6.3. Only the comments, docstrings, and this README are in English; the code is identical to the Korean-comment edition.*
