#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
brain=Brain()

# Robot configuration code
# AI Classification Competition Element IDs - Override
class GameElementsOverride:
    RED_BLUE_PIN = 0
    BLUE_YELLOW_PIN = 1
    RED_YELLOW_PIN = 2
    YELLOW_PIN = 3
    CUP = 4
# AI Vision Color Descriptions
# AI Vision Code Descriptions
ai_vision_10 = AiVision(Ports.PORT10, AiVision.ALL_AIOBJS)
controller_1 = Controller(PRIMARY)


# wait for rotation sensor to fully initialize
wait(30, MSEC)


# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))

# Set random seed
initializeRandomSeed()


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

#endregion VEXcode Generated Robot Configuration


# ======================================================================
# OVERRIDE ROBOT
# Arcade drive, 2-motor DR4B lift, claw and AI Vision.
#
# Controls:
#   Right stick - drive (up = forward, sideways = turn).
#                 Driving with the stick straight up keeps the robot straight.
#   Left stick  - lift up / down, holds where you let go,
#                 stops at the top and bottom limits
#   L1          - claw: press to grab, press again to release
#   R1 / R2     - claw manual: hold to close / open
#   L2 (hold)   - lift limits off, also lets the lift move before calibration
#   Up / Down   - lift smoothly to the Toggle height / all the way down
#                 (moving the left stick takes over)
#   B           - calibrate: claw open/closed limits, then the lift bottom
#   A           - OK the missing devices (e.g. no vision sensor mounted),
#                 so they stop warning
#   X           - test the selected autonomous, X again stops it.
#                 Only works with no field or competition switch plugged in.
#   Brain tap   - choose the autonomous routine
#
# Startup: the team logo plays on the Brain screen and controller, then
# the controller asks you to press B. The lift drives down slowly until
# it stops, calls that 0, and the controller shows READY.
# The lift stick does nothing until this is done.
# In a match nobody can press B and the robot starts disabled, so if it
# hasn't been calibrated, autonomous takes the lift's starting position
# as the bottom (it must start folded to fit 18") without moving anything.
# Calibrating with B before connecting to the field is more exact: it
# stays valid as long as the program keeps running.
# ======================================================================


# ----------------------------------------------------------------------
# Motors
# The controller and AI Vision are set up in the Devices panel above.
# Don't add these motors there as well.
# ----------------------------------------------------------------------

DRIVE_CARTRIDGE = GearSetting.RATIO_18_1 # green
LIFT_CARTRIDGE = GearSetting.RATIO_18_1 # green
CLAW_CARTRIDGE = GearSetting.RATIO_18_1 # green

left_drive = Motor(Ports.PORT11, DRIVE_CARTRIDGE, False)
right_drive = Motor(Ports.PORT1, DRIVE_CARTRIDGE, True)

# One lift motor per side. They face opposite ways, so one is reversed.
lift_left = Motor(Ports.PORT12, LIFT_CARTRIDGE, True)
lift_right = Motor(Ports.PORT2, LIFT_CARTRIDGE, False)
lift = MotorGroup(lift_left, lift_right)
lift_motors = [lift_left, lift_right]

claw_motor = Motor(Ports.PORT5, CLAW_CARTRIDGE, False) # forward closes the claw

# Everything checked for loose cables, with the name shown on screen.
DEVICES = [
    ("DRIVE L", left_drive),
    ("DRIVE R", right_drive),
    ("LIFT L", lift_left),
    ("LIFT R", lift_right),
    ("CLAW", claw_motor),
    ("VISION", ai_vision_10),
]


# ----------------------------------------------------------------------
# Tuning
# ----------------------------------------------------------------------

# Stick feel
STICK_DEADBAND = 3 # % of stick travel ignored around the center
DRIVE_CURVE = 0.5 # 0 = linear, 1 = cubic. Higher gives finer slow control
TURN_SCALE = 0.5 # turning at full strength is too twitchy

# Acceleration ramp, in % change per 20 ms loop.
# 10 means 0 -> 100 % takes 0.2 s. Smaller is smoother but feels laggy.
DRIVE_ACCEL_STEP = 6 # speeding up
DRIVE_DECEL_STEP = 10 # slowing down, a bit quicker so stops stay sharp

# Lift height limit, in lift motor degrees above the calibrated bottom.
LIFT_MAX_DEG = 300 # keep it a little below the mechanical top
LIFT_SLOW_ZONE = 30 # start slowing down this many degrees before the top or bottom
LIFT_SLOW_MIN = 0.25 # slowest speed multiplier right at a limit

# Lift calibration (finding the bottom)
CAL_VOLTS = 3 # how hard to drive down, gravity helps too
CAL_START_MS = 300 # give the lift time to start moving before checking
CAL_STALL_RPM = 5 # slower than this counts as stopped
CAL_STALL_MS = 200 # must stay stopped this long to count as the bottom
CAL_TIMEOUT_MS = 3000 # give up after this long

# Lift, manual
LIFT_MAX_SPEED = 75 # % at full stick
LIFT_DOWN_SCALE = 0.3 # going down slower so it doesn't slam

# Slow the drive down as the lift goes up, so a tall robot doesn't tip.
LIFT_UP_DRIVE_SCALE = 0.5 # drive speed multiplier with the lift at LIFT_MAX_DEG

# Claw. Voltage control, so the grip force stays the same even when
# the claw is stalled against a pin.
CLAW_TORQUE = 60 # % max torque, protects the motor
CLAW_CLOSE_VOLTS = 6 # strength while closing
CLAW_CLOSE_MS = 400 # how long to close at full strength
CLAW_SQUEEZE_VOLTS = 2 # light grip that keeps a pin from slipping
CLAW_OPEN_VOLTS = 6 # strength while opening
CLAW_OPEN_MS = 400 # how long to open before holding still
CLAW_MANUAL_VOLTS = 4 # strength when holding R1 / R2

# Claw calibration (part of B). Fully open = 0, closing counts up.
CALIBRATE_CLAW = True # False = calibrate only the lift
CLAW_CAL_VOLTS = 4 # how hard to push against the open and closed stops
CLAW_CAL_TIMEOUT_MS = 2000 # give up on a step after this long
CLAW_MIN_TRAVEL = 30 # less travel than this means calibration went wrong
CLAW_OPEN_DEG = 10 # "open" stops this far short of the open stop, so it doesn't press on it
CLAW_OPEN_SPEED = 60 # % when opening to CLAW_OPEN_DEG
CLAW_HOLD_MARGIN = 15 # closed but this far short of empty-closed = holding something

# Vision. Used in autonomous, and shown on the Brain screen.
WANTED_IDS = [ # which elements count as targets
    GameElementsOverride.RED_BLUE_PIN,
    GameElementsOverride.BLUE_YELLOW_PIN,
    GameElementsOverride.RED_YELLOW_PIN,
    GameElementsOverride.YELLOW_PIN,
]
SENSOR_CENTER_X = 160 # the AI Vision image is 320 px wide
ALIGN_TOLERANCE = 10 # px off centre that still counts as aimed
VISION_MAX_TURN = 35 # % strongest turn while aiming
CLOSE_HEIGHT = 110 # px box height when a pin is right in front of the claw, measure it
APPROACH_SPEED = 30 # % while driving at a pin
FINAL_PUSH_CM = 5 # creep forward this much before grabbing

# Drivetrain measurements, used to turn cm and degrees into wheel turns.
# Check them on the robot, then fine-tune with the two test routines.
WHEEL_DIAMETER_CM = 10.16 # 4" wheels. 3.25" = 8.26, 2.75" = 6.99
DRIVE_MOTOR_TEETH = 72 # gear on the motor
DRIVE_WHEEL_TEETH = 84 # gear on the wheel axle
TRACK_WIDTH_CM = 30.0 # left wheel to right wheel, centre to centre
DRIVE_DISTANCE_FIX = 1.0 # "Test drive" went X cm instead of 100 -> set to 100 / X
TURN_FIX = 1.0 # "Test turn" turned X degrees instead of 90 -> set to 90 / X

# Autonomous motion
AUTO_DRIVE_SPEED = 60 # % top speed when driving a distance
AUTO_TURN_SPEED = 45 # % top speed when turning
AUTO_MIN_SPEED = 8 # % slowest push, so it doesn't stall just short of the target
AUTO_DRIVE_TOLERANCE_CM = 1.0 # close enough to the distance
AUTO_TURN_TOLERANCE_DEG = 2 # close enough to the angle
AUTO_SETTLE_MS = 100 # must stay inside the tolerance this long to count as done
AUTO_LIFT_SPEED = 60 # %
AUTO_LIFT_TOLERANCE = 8 # lift motor degrees
LIFT_CARRY_DEG = 40 # lift height for driving with a pin
AUTON_GRAB_PRELOAD = True # squeeze the preload as autonomous starts

# Up / Down arrows in driver control: smooth lift moves for the Toggle.
# Measure TOGGLE_LIFT_DEG: hold the claw level with a Toggle (or something
# the same height) and read "Lift" on the Brain screen.
TOGGLE_LIFT_DEG = 120 # lift height that lines the claw up with the Toggle
LIFT_GOTO_UP_SPEED = 35 # % top speed going up
LIFT_GOTO_DOWN_SPEED = 20 # % top speed going down
LIFT_GOTO_ACCEL = 3 # % more speed per 20 ms loop, so 0 -> 35 % takes about 0.25 s
LIFT_GOTO_SLOW_DEG = 40 # start slowing down this many degrees before the target
LIFT_GOTO_MIN_SPEED = 6 # % slowest, so it still gets all the way there
LIFT_GOTO_TOLERANCE = 3 # degrees close enough, then the motors hold

# Startup intro: the team logo wipes in on the Brain screen and controller. False skips it.
STARTUP_INTRO = True
INTRO_WIPE_MS = 700 # how long the wipe-in takes
INTRO_HOLD_MS = 1000 # how long the finished logo stays up

# Warn the driver when motors get this hot.
HOT_TEMP_C = 55


# ----------------------------------------------------------------------
# PID gains
# Tuning order: start with only KP, raise it until the robot starts to
# wobble around the target, then back off a bit. Add KD to calm the
# wobble. Add KI only if it keeps stopping a little short of the target.
# ----------------------------------------------------------------------

# Driving straight. Error = how many degrees the left wheels got ahead
# of the right ones since you stopped turning. Output in % turn.
STRAIGHT_ASSIST = True # False turns this off
STRAIGHT_KP = 0.4
STRAIGHT_KI = 0.0
STRAIGHT_KD = 0.0
STRAIGHT_MAX = 15 # % strongest correction

# Autonomous: driving a distance. Error in motor degrees, output in % speed.
AUTO_DRIVE_KP = 0.25
AUTO_DRIVE_KI = 0.0
AUTO_DRIVE_KD = 0.02

# Autonomous: turning. Error in motor degrees of left-right wheel difference,
# output in % turn.
AUTO_TURN_KP = 0.3
AUTO_TURN_KI = 0.0
AUTO_TURN_KD = 0.02

# Autonomous: aiming at a pin. Error in pixels, output in % turn.
VISION_KP = 0.35
VISION_KI = 0.0
VISION_KD = 0.03


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------

def clamp(value, low, high):
    return max(low, min(high, value))


def deadband(value):
    # Ignore tiny stick movements so the robot doesn't creep.
    return 0 if abs(value) < STICK_DEADBAND else value


def curve(value):
    # Mix of linear and cubic: gentle near the center, full speed at the edge.
    x = value / 100
    return 100 * ((1 - DRIVE_CURVE) * x + DRIVE_CURVE * x * x * x)


def robot_enabled():
    # False while the field (or competition switch) has the robot disabled.
    try:
        return competition.is_enabled()
    except Exception:
        return True


# ----------------------------------------------------------------------
# PID controller
# ----------------------------------------------------------------------

class PID:
    # output = KP * error + KI * (error added up over time) + KD * (how fast error changes)
    # P pushes toward the target, I fixes a small leftover error,
    # D brakes when the error is shrinking fast so it doesn't overshoot.

    def __init__(self, kp, ki, kd, i_max=20, d_smoothing=0.5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_max = i_max # biggest output the I part may add, in output units
        self.d_smoothing = d_smoothing # 0 = raw D, closer to 1 = smoother D
        self.reset()

    def reset(self):
        self.integral = 0
        self.last_error = None
        self.derivative = 0

    def update(self, error, dt):
        # error: target minus current value, dt: seconds since the last update
        if self.ki != 0:
            self.integral += error * dt
            limit = abs(self.i_max / self.ki)
            self.integral = clamp(self.integral, -limit, limit)

        if self.last_error is None or dt <= 0:
            raw_derivative = 0
        else:
            raw_derivative = (error - self.last_error) / dt
        # Smooth the D part, sensor readings are a bit jumpy
        self.derivative = self.d_smoothing * self.derivative + (1 - self.d_smoothing) * raw_derivative
        self.last_error = error

        return self.kp * error + self.ki * self.integral + self.kd * self.derivative


# ----------------------------------------------------------------------
# Drive
# ----------------------------------------------------------------------

# Current drive outputs in %, remembered between loops for the ramp.
drive_left_out = 0
drive_right_out = 0


def ramp(current, target):
    # Move current toward target by at most one step per loop.
    if abs(target) > abs(current):
        step = DRIVE_ACCEL_STEP
    else:
        step = DRIVE_DECEL_STEP
    return current + clamp(target - current, -step, step)


def arcade(forward, turn):
    # Drive with forward and turn in %. If the sum goes past 100 %,
    # both sides are scaled down together so the turn isn't lost.
    global drive_left_out, drive_right_out
    left = forward + turn
    right = forward - turn
    biggest = max(abs(left), abs(right), 100)
    left = left * 100 / biggest
    right = right * 100 / biggest

    drive_left_out = ramp(drive_left_out, left)
    drive_right_out = ramp(drive_right_out, right)
    left_drive.spin(FORWARD, drive_left_out, PERCENT)
    right_drive.spin(FORWARD, drive_right_out, PERCENT)


def stop_drive():
    global drive_left_out, drive_right_out
    drive_left_out = 0
    drive_right_out = 0
    left_drive.stop(BRAKE)
    right_drive.stop(BRAKE)


def wheel_difference():
    # How many degrees the left side has turned more than the right side.
    return left_drive.position(DEGREES) - right_drive.position(DEGREES)


def lift_drive_scale():
    # 1.0 with the lift down, LIFT_UP_DRIVE_SCALE with it at the top limit.
    height = clamp(lift.position(DEGREES) / LIFT_MAX_DEG, 0, 1)
    return 1 - (1 - LIFT_UP_DRIVE_SCALE) * height


# ----------------------------------------------------------------------
# Lift
# ----------------------------------------------------------------------

# Calibration state, shown on the screens:
# "not calibrated", "calibrating", "ok", "failed" (about the lift), or
# "assumed" = lift zero taken from where it started, without moving it
lift_status = "not calibrated"
lift_ready_at = -10000 # time calibration finished, for the READY message

# Claw position (claw motor degrees from fully open) when it closes on
# nothing. None = the claw isn't calibrated, it then opens on a timer instead.
claw_closed_deg = None
claw_status = "not calibrated" # "ok" or "failed" once calibration has run


class Calibration:
    # The startup calibration (B), one step at a time so driving still works:
    #   1. claw opens until it stops       -> that's claw 0, fully open
    #   2. claw closes until it stops      -> how far it closes with nothing in it
    #   3. claw goes back to open and stays there
    #   4. lift drives down until it stops -> that's lift 0
    # The claw goes first so the lift comes down with the claw open.
    # Call start() once, then update() every loop until it returns True.

    def __init__(self):
        self.active = False
        self.step = 0
        self.step_start = 0
        self.stopped_since = None

    def start(self):
        global lift_status
        self.active = True
        lift_status = "calibrating"
        self.next_step(1 if CALIBRATE_CLAW else 4)

    def next_step(self, step):
        self.step = step
        self.step_start = brain.timer.time(MSEC)
        self.stopped_since = None
        if step == 3:
            claw.open_now()

    def stall_check(self, motors, now, timeout_ms):
        # "stopped" once the motors have stood still long enough,
        # "timeout" if they never did, "" while still moving.
        elapsed = now - self.step_start
        speed = max(abs(m.velocity(VelocityUnits.RPM)) for m in motors)
        if elapsed >= CAL_START_MS and speed < CAL_STALL_RPM:
            if self.stopped_since is None:
                self.stopped_since = now
            elif now - self.stopped_since >= CAL_STALL_MS:
                return "stopped"
        else:
            self.stopped_since = None
        if elapsed >= timeout_ms:
            return "timeout"
        return ""

    def update(self):
        # Returns True when calibration is finished.
        global claw_closed_deg, claw_status
        now = brain.timer.time(MSEC)

        if self.step == 1: # claw: find fully open
            claw_motor.spin(REVERSE, CLAW_CAL_VOLTS, VoltageUnits.VOLT)
            result = self.stall_check([claw_motor], now, CLAW_CAL_TIMEOUT_MS)
            if result == "stopped":
                claw_motor.set_position(0, DEGREES)
                self.next_step(2)
            elif result == "timeout":
                claw_closed_deg = None
                claw_status = "failed"
                self.next_step(3)

        elif self.step == 2: # claw: find closed on nothing
            claw_motor.spin(FORWARD, CLAW_CAL_VOLTS, VoltageUnits.VOLT)
            result = self.stall_check([claw_motor], now, CLAW_CAL_TIMEOUT_MS)
            if result:
                travel = claw_motor.position(DEGREES)
                if result == "stopped" and travel >= CLAW_MIN_TRAVEL:
                    claw_closed_deg = travel
                    claw_status = "ok"
                else:
                    # Never stopped, or barely moved: something is wrong
                    claw_closed_deg = None
                    claw_status = "failed"
                print("claw calibration:", claw_status, "travel", int(travel), "deg")
                self.next_step(3)

        elif self.step == 3: # claw: back to open, and wait until it's there
            claw.update(now, False, False)
            elapsed = now - self.step_start
            if claw_closed_deg is not None:
                opened = abs(claw_motor.position(DEGREES) - CLAW_OPEN_DEG) < 5
            else:
                opened = elapsed >= CLAW_OPEN_MS # not calibrated: open on the timer
            if opened or elapsed > CLAW_CAL_TIMEOUT_MS:
                self.next_step(4)

        elif self.step == 4: # lift: find the bottom
            lift.spin(REVERSE, CAL_VOLTS, VoltageUnits.VOLT)
            result = self.stall_check(lift_motors, now, CAL_TIMEOUT_MS)
            if result:
                self.finish(result == "stopped")
                return True
        return False

    def finish(self, found_bottom):
        global lift_status, lift_ready_at
        self.active = False
        lift.set_position(0, DEGREES)
        lift.stop(HOLD)
        if found_bottom:
            lift_status = "ok"
            lift_ready_at = brain.timer.time(MSEC)
            controller_1.rumble("..")
        else:
            # Probably stuck or unplugged. 0 is set anyway as a best guess.
            lift_status = "failed"
            controller_1.rumble("-.-")


calibration = Calibration()


def calibrate_now():
    # Blocking version of B. Takes about 1 - 3 s and opens the claw.
    calibration.start()
    while not calibration.update():
        wait(20, MSEC)


def zero_lift_here():
    # Instant, no movement: call wherever the lift is now its bottom.
    # Used at the start of autonomous, where the robot must start folded
    # inside 18" and a full calibration would drop the preload.
    global lift_status
    lift.set_position(0, DEGREES)
    lift.stop(HOLD)
    lift_status = "assumed"
    print("lift zero taken from the start position")


def limit_lift_speed(speed):
    # Takes the wanted lift speed in % (positive = up) and returns a safe one:
    # 0 at a limit, and slower inside the slow zone near a limit.
    pos = lift.position(DEGREES)
    if speed > 0:
        room = LIFT_MAX_DEG - pos
    elif speed < 0:
        room = pos
    else:
        return 0

    if room <= 0:
        return 0
    if room < LIFT_SLOW_ZONE:
        speed *= max(LIFT_SLOW_MIN, room / LIFT_SLOW_ZONE)
    return speed


def smooth_lift_step(goal, speed_now):
    # One 20 ms step of a gentle lift move to goal (lift motor degrees):
    # speeds up a little each step, slows down near the goal. Returns the
    # new speed in %, or None once it has arrived (the motors then hold).
    goal = clamp(goal, 0, LIFT_MAX_DEG)
    error = goal - lift.position(DEGREES)
    if abs(error) <= LIFT_GOTO_TOLERANCE:
        lift.stop(HOLD)
        return None
    top = LIFT_GOTO_UP_SPEED if error > 0 else LIFT_GOTO_DOWN_SPEED
    wanted = clamp(error / LIFT_GOTO_SLOW_DEG, -1, 1) * top # slows down near the goal
    if abs(wanted) < LIFT_GOTO_MIN_SPEED:
        wanted = LIFT_GOTO_MIN_SPEED if error > 0 else -LIFT_GOTO_MIN_SPEED
    speed = speed_now + clamp(wanted - speed_now, -LIFT_GOTO_ACCEL, LIFT_GOTO_ACCEL)
    lift.spin(FORWARD, speed, PERCENT)
    return speed


# ----------------------------------------------------------------------
# Claw
# ----------------------------------------------------------------------

class Claw:
    # Toggle (L1): close hard for a moment, then keep a light squeeze.
    # Release: once calibrated, go to the open position (CLAW_OPEN_DEG);
    # before that, open on a timer and hold still.
    # Manual (R1 / R2): direct control while held.

    def __init__(self):
        self.closed = False
        self.changed_at = -CLAW_OPEN_MS # so it doesn't open by itself at start
        self.open_action = "done" # "goto" = send it to the open position, "hold" = stay put

    def toggle(self, now):
        self.closed = not self.closed
        self.changed_at = now
        if not self.closed:
            self.open_action = "goto"

    def open_now(self):
        # Open straight away (calibration and autonomous use this).
        self.closed = False
        self.changed_at = brain.timer.time(MSEC)
        self.open_action = "goto"
        self.update(self.changed_at, False, False)

    def holding(self):
        # True when closed and stopped clearly short of where it closes on
        # nothing, so something is in the claw. Needs a calibrated claw.
        if not self.closed or claw_closed_deg is None:
            return False
        if brain.timer.time(MSEC) - self.changed_at < CLAW_CLOSE_MS:
            return False # still closing
        return claw_motor.position(DEGREES) < claw_closed_deg - CLAW_HOLD_MARGIN

    def state_text(self):
        if not self.closed:
            return "open"
        if claw_closed_deg is None:
            return "closed"
        return "holding" if self.holding() else "closed, empty"

    def update(self, now, manual_close, manual_open):
        if manual_close:
            claw_motor.spin(FORWARD, CLAW_MANUAL_VOLTS, VoltageUnits.VOLT)
            self.closed = True
            self.changed_at = now - CLAW_CLOSE_MS # skip straight to squeezing
            return
        if manual_open:
            claw_motor.spin(REVERSE, CLAW_MANUAL_VOLTS, VoltageUnits.VOLT)
            self.closed = False
            self.changed_at = now - CLAW_OPEN_MS
            self.open_action = "hold" # stay where you let go
            return

        elapsed = now - self.changed_at
        if self.closed:
            volts = CLAW_CLOSE_VOLTS if elapsed < CLAW_CLOSE_MS else CLAW_SQUEEZE_VOLTS
            claw_motor.spin(FORWARD, volts, VoltageUnits.VOLT)
        elif self.open_action == "hold":
            claw_motor.stop(HOLD)
            self.open_action = "done"
        elif claw_closed_deg is not None:
            # Calibrated: the motor drives to the open position and holds it
            if self.open_action == "goto":
                claw_motor.spin_to_position(CLAW_OPEN_DEG, DEGREES, CLAW_OPEN_SPEED, PERCENT, wait=False)
                self.open_action = "done"
        elif elapsed < CLAW_OPEN_MS:
            claw_motor.spin(REVERSE, CLAW_OPEN_VOLTS, VoltageUnits.VOLT)
        else:
            claw_motor.stop(HOLD)


claw = Claw()


# ----------------------------------------------------------------------
# Vision
# ----------------------------------------------------------------------

def vision_connected():
    try:
        return ai_vision_10.installed()
    except Exception:
        return True


def find_target():
    # The biggest wanted element in view (usually the closest), or None.
    # Also None when the vision sensor isn't plugged in.
    if not vision_connected():
        return None
    objs = ai_vision_10.take_snapshot(AiVision.ALL_AIOBJS)
    if not objs:
        return None
    best = None
    best_area = -1
    for o in objs:
        if not getattr(o, "exists", True):
            continue
        if o.id not in WANTED_IDS:
            continue
        area = o.width * o.height
        if area > best_area:
            best_area = area
            best = o
    return best


# ----------------------------------------------------------------------
# Autonomous: building blocks
# Every move has a timeout, so a stuck robot never hangs the routine.
# Each one returns True if it finished, False if it timed out or was stopped.
# ----------------------------------------------------------------------

# How far the robot moves per motor degree
CM_PER_MOTOR_DEG = (math.pi * WHEEL_DIAMETER_CM / 360
                    * DRIVE_MOTOR_TEETH / DRIVE_WHEEL_TEETH * DRIVE_DISTANCE_FIX)

auton_running = False # a routine is running (match or test)
auton_test_running = False # it's a test started with X
auton_aborted = False # the test was stopped with X


def auton_stopped():
    # True once a test run is stopped with X. Every move checks this, so
    # the rest of the routine finishes straight away.
    global auton_aborted
    if auton_test_running and controller_1.buttonX.pressing():
        auton_aborted = True
    return auton_aborted


def match_control_connected():
    # True with a field controller or competition switch plugged in.
    # If it can't tell, it says True, so X tests stay off to be safe.
    try:
        return competition.is_field_control() or competition.is_competition_switch()
    except Exception:
        return True


def robot_deg_to_wheel_diff(angle):
    # Left-right wheel difference (motor degrees) for turning the robot
    # this many degrees in place. Each side rolls along a circle with
    # the track width as its diameter, one forward and one back.
    arc_cm = math.pi * TRACK_WIDTH_CM * angle / 360
    return 2 * arc_cm / CM_PER_MOTOR_DEG * TURN_FIX


def settle(error, tolerance, inside_since, now):
    # Keeps track of how long the error has stayed inside the tolerance.
    # Returns the new inside_since (None if outside).
    if abs(error) >= tolerance:
        return None
    if inside_since is None:
        return now
    return inside_since


def with_min_speed(output, error, tolerance):
    # Small PID outputs can't overcome friction, so push at least AUTO_MIN_SPEED
    # until the target is reached.
    if abs(error) >= tolerance and abs(output) < AUTO_MIN_SPEED:
        return AUTO_MIN_SPEED if error > 0 else -AUTO_MIN_SPEED
    return output


def drive_cm(distance_cm, max_speed=AUTO_DRIVE_SPEED, timeout_ms=3000):
    # Drives straight, negative = backwards, and holds the heading.
    target = distance_cm / CM_PER_MOTOR_DEG
    tolerance = AUTO_DRIVE_TOLERANCE_CM / CM_PER_MOTOR_DEG
    start_left = left_drive.position(DEGREES)
    start_right = right_drive.position(DEGREES)
    start_diff = wheel_difference()
    distance_pid = PID(AUTO_DRIVE_KP, AUTO_DRIVE_KI, AUTO_DRIVE_KD)
    heading_pid = PID(STRAIGHT_KP, STRAIGHT_KI, STRAIGHT_KD)

    start = brain.timer.time(MSEC)
    last = start
    inside_since = None
    done = False
    while not auton_stopped():
        now = brain.timer.time(MSEC)
        dt = max(now - last, 1) / 1000
        last = now

        traveled = (left_drive.position(DEGREES) - start_left
                    + right_drive.position(DEGREES) - start_right) / 2
        error = target - traveled
        inside_since = settle(error, tolerance, inside_since, now)
        if inside_since is not None and now - inside_since >= AUTO_SETTLE_MS:
            done = True
            break
        if now - start > timeout_ms:
            break

        forward = clamp(distance_pid.update(error, dt), -max_speed, max_speed)
        forward = with_min_speed(forward, error, tolerance)
        drift = wheel_difference() - start_diff # positive = drifting right
        turn = clamp(-heading_pid.update(drift, dt), -STRAIGHT_MAX, STRAIGHT_MAX)
        arcade(forward, turn)
        wait(10, MSEC)

    stop_drive()
    return done


def turn_deg(angle, max_speed=AUTO_TURN_SPEED, timeout_ms=2000):
    # Turns in place, positive = right (clockwise), negative = left.
    # Uses the wheel encoders, so wheel slip makes it less exact than an
    # inertial sensor would be. TURN_FIX corrects the average error.
    target = robot_deg_to_wheel_diff(angle)
    tolerance = robot_deg_to_wheel_diff(AUTO_TURN_TOLERANCE_DEG)
    start_diff = wheel_difference()
    turn_pid = PID(AUTO_TURN_KP, AUTO_TURN_KI, AUTO_TURN_KD)

    start = brain.timer.time(MSEC)
    last = start
    inside_since = None
    done = False
    while not auton_stopped():
        now = brain.timer.time(MSEC)
        dt = max(now - last, 1) / 1000
        last = now

        error = target - (wheel_difference() - start_diff)
        inside_since = settle(error, tolerance, inside_since, now)
        if inside_since is not None and now - inside_since >= AUTO_SETTLE_MS:
            done = True
            break
        if now - start > timeout_ms:
            break

        turn = clamp(turn_pid.update(error, dt), -max_speed, max_speed)
        turn = with_min_speed(turn, error, tolerance)
        arcade(0, turn)
        wait(10, MSEC)

    stop_drive()
    return done


def lift_to(height_deg, timeout_ms=2000):
    # Moves the lift to a height (lift motor degrees above the bottom),
    # using the motors' own position control. Waits until it's there.
    target = clamp(height_deg, 0, LIFT_MAX_DEG)
    lift.spin_to_position(target, DEGREES, AUTO_LIFT_SPEED, PERCENT, wait=False)
    start = brain.timer.time(MSEC)
    while abs(lift.position(DEGREES) - target) > AUTO_LIFT_TOLERANCE:
        if auton_stopped() or brain.timer.time(MSEC) - start > timeout_ms:
            lift.stop(HOLD)
            return False
        wait(20, MSEC)
    return True # close enough to carry on, the motors finish the last bit and hold


def claw_grab():
    # Close hard, then keep the light squeeze (same as L1 in driver control).
    # Returns False if the calibrated claw closed on nothing (missed the pin).
    claw_motor.spin(FORWARD, CLAW_CLOSE_VOLTS, VoltageUnits.VOLT)
    wait(CLAW_CLOSE_MS, MSEC)
    claw_motor.spin(FORWARD, CLAW_SQUEEZE_VOLTS, VoltageUnits.VOLT)
    claw.closed = True
    claw.changed_at = brain.timer.time(MSEC) - CLAW_CLOSE_MS # driver control keeps squeezing
    if claw_closed_deg is None:
        return True # can't tell without calibration
    return claw.holding()


def claw_release():
    claw.open_now()
    wait(CLAW_OPEN_MS, MSEC)


def aim_at_target(timeout_ms=1500):
    # Turns until the nearest wanted element is in the middle of the camera.
    # False with no vision sensor, nothing in view, or out of time.
    if not vision_connected():
        print("aim_at_target: no vision sensor, skipping")
        return False
    aim_pid = PID(VISION_KP, VISION_KI, VISION_KD)
    start = brain.timer.time(MSEC)
    last = start
    inside_since = None
    done = False
    while not auton_stopped():
        now = brain.timer.time(MSEC)
        dt = max(now - last, 1) / 1000
        last = now
        if now - start > timeout_ms:
            break

        target = find_target()
        if target is None:
            stop_drive() # nothing in view, wait and look again
            aim_pid.reset()
            inside_since = None
        else:
            error = target.centerX - SENSOR_CENTER_X # positive = target is to the right
            inside_since = settle(error, ALIGN_TOLERANCE, inside_since, now)
            if inside_since is not None and now - inside_since >= AUTO_SETTLE_MS:
                done = True
                break
            turn = clamp(aim_pid.update(error, dt), -VISION_MAX_TURN, VISION_MAX_TURN)
            arcade(0, with_min_speed(turn, error, ALIGN_TOLERANCE))
        wait(20, MSEC)

    stop_drive()
    return done


def drive_to_target(timeout_ms=3000):
    # Drives at the nearest wanted element, steering to keep it centred,
    # until it's close enough to grab (box taller than CLOSE_HEIGHT).
    if not vision_connected():
        return False
    aim_pid = PID(VISION_KP, VISION_KI, VISION_KD)
    start = brain.timer.time(MSEC)
    last = start
    last_height = 0
    reached = False
    while not auton_stopped():
        now = brain.timer.time(MSEC)
        dt = max(now - last, 1) / 1000
        last = now
        if now - start > timeout_ms:
            break

        target = find_target()
        if target is None:
            if last_height > CLOSE_HEIGHT * 0.7:
                reached = True # it was almost in reach and dropped below the camera
                break
            stop_drive()
            aim_pid.reset()
        else:
            last_height = target.height
            if target.height >= CLOSE_HEIGHT:
                reached = True
                break
            error = target.centerX - SENSOR_CENTER_X
            turn = clamp(aim_pid.update(error, dt), -VISION_MAX_TURN, VISION_MAX_TURN)
            arcade(APPROACH_SPEED, turn)
        wait(20, MSEC)

    stop_drive()
    return reached


def pick_up_with_vision():
    # Find the nearest pin in front, drive to it, grab it and lift it a bit.
    # False if it couldn't (no vision, nothing seen, out of time).
    claw_release()
    lift_to(0)
    if not aim_at_target():
        return False
    if not drive_to_target():
        return False
    drive_cm(FINAL_PUSH_CM, APPROACH_SPEED, 1000)
    if not claw_grab():
        print("pick_up_with_vision: claw closed on nothing")
        claw_release()
        return False
    lift_to(LIFT_CARRY_DEG)
    return True


# ----------------------------------------------------------------------
# Autonomous: routines
# Add a routine by writing a function and adding it to AUTONS.
# Names are shown on the controller, keep them 13 characters or less.
# ----------------------------------------------------------------------

def auton_nothing():
    pass # stays still, the safe choice


def auton_test_drive():
    # Drives 100 cm. Measure how far it really went and set DRIVE_DISTANCE_FIX.
    drive_cm(100)


def auton_test_turn():
    # Turns 90° right, waits, turns back. Check the angle and set TURN_FIX.
    turn_deg(90)
    wait(1000, MSEC)
    turn_deg(-90)


def auton_vision_pickup():
    # Picks up the nearest pin in front of the robot. Opens the claw first,
    # so it drops the preload where the robot starts: a test routine.
    pick_up_with_vision()


def auton_example_route():
    # TEMPLATE showing what a route looks like. The distances and angles are
    # made up: replace them with your real plan before using it in a match.
    drive_cm(60)
    turn_deg(-45)
    if not pick_up_with_vision():
        # No vision sensor or no pin seen: grab blind straight ahead
        drive_cm(20)
        claw_grab()
        lift_to(LIFT_CARRY_DEG)
    drive_cm(-30)
    turn_deg(90)
    lift_to(200)
    drive_cm(25)
    claw_release()
    drive_cm(-20)
    lift_to(0)


AUTONS = [
    ("Nothing", auton_nothing),
    ("Vision pickup", auton_vision_pickup),
    ("Example route", auton_example_route),
    ("Test drive", auton_test_drive),
    ("Test turn", auton_test_turn),
]
selected_auton = 0


def next_auton():
    # Brain screen tap: choose the next routine. Ignored while one is running.
    global selected_auton
    if not auton_running:
        selected_auton = (selected_auton + 1) % len(AUTONS)


def run_selected_auton():
    global auton_running, auton_aborted
    auton_running = True
    auton_aborted = False
    name = AUTONS[selected_auton][0]
    routine = AUTONS[selected_auton][1]
    print("autonomous:", name)
    try:
        if lift_status not in ("ok", "assumed"):
            zero_lift_here()
        if AUTON_GRAB_PRELOAD:
            claw_grab() # squeeze the preload, the grip was off while disabled
        routine()
    finally:
        stop_drive()
        auton_running = False


def run_auton_test():
    # Runs the selected routine from driver control (X). Pressing X again stops it.
    global auton_test_running
    while controller_1.buttonX.pressing():
        wait(20, MSEC) # let go of X first, the next press means stop
    auton_test_running = True
    try:
        run_selected_auton()
    finally:
        auton_test_running = False
    while controller_1.buttonX.pressing():
        wait(20, MSEC) # don't start again straight away


def autonomous():
    run_selected_auton()


# ----------------------------------------------------------------------
# Driver control
# ----------------------------------------------------------------------

def user_control():
    straight_pid = PID(STRAIGHT_KP, STRAIGHT_KI, STRAIGHT_KD)

    straight_active = False
    straight_start = 0 # wheel difference when driving straight began
    l1_was_pressed = False
    b_was_pressed = False
    x_was_pressed = False
    up_was_pressed = False
    down_was_pressed = False
    lift_goal = None # height the arrows sent the lift to, None = stick control
    lift_goto_out = 0 # current speed of that move, in %
    last_time = brain.timer.time(MSEC)

    while True:
        now = brain.timer.time(MSEC)
        dt = max(now - last_time, 1) / 1000 # seconds since the last loop
        last_time = now

        # ---- Drive: right stick, slower when the lift is up ----
        forward = curve(deadband(controller_1.axis2.position()))
        turn = curve(deadband(controller_1.axis1.position())) * TURN_SCALE

        # Straight assist: no turn on the stick, so keep both sides even
        if STRAIGHT_ASSIST and turn == 0 and forward != 0:
            if not straight_active:
                straight_active = True
                straight_start = wheel_difference()
                straight_pid.reset()
            drift = wheel_difference() - straight_start # positive = drifting right
            turn = clamp(-straight_pid.update(drift, dt), -STRAIGHT_MAX, STRAIGHT_MAX)
        else:
            straight_active = False

        scale = lift_drive_scale()
        arcade(forward * scale, turn * scale)

        # ---- Lift ----
        # B: start calibration (first time, or again if something slipped)
        b_pressed = controller_1.buttonB.pressing()
        if b_pressed and not b_was_pressed and not calibration.active:
            calibration.start()
            lift_goal = None
        b_was_pressed = b_pressed

        # Up / Down arrows: lift to the Toggle height / all the way down.
        # Needs a calibrated lift. Moving the left stick takes over again.
        lift_known = lift_status in ("ok", "assumed")
        up_pressed = controller_1.buttonUp.pressing()
        down_pressed = controller_1.buttonDown.pressing()
        if lift_known and not calibration.active:
            if up_pressed and not up_was_pressed:
                lift_goal = TOGGLE_LIFT_DEG
            elif down_pressed and not down_was_pressed:
                lift_goal = 0
        up_was_pressed = up_pressed
        down_was_pressed = down_pressed

        limits_off = controller_1.buttonL2.pressing()
        lift_stick = deadband(controller_1.axis3.position())
        if lift_stick != 0:
            lift_goal = None # the driver takes over
        if lift_goal is None:
            lift_goto_out = 0
        if calibration.active:
            calibration.update() # sticks for lift and claw are ignored until it's done
        elif lift_goal is not None:
            lift_goto_out = smooth_lift_step(lift_goal, lift_goto_out)
            if lift_goto_out is None:
                lift_goal = None # arrived, the motors hold it there
                lift_goto_out = 0
        elif lift_known or limits_off:
            lift_speed = lift_stick * LIFT_MAX_SPEED / 100
            if lift_speed < 0:
                lift_speed *= LIFT_DOWN_SCALE
            if not limits_off:
                lift_speed = limit_lift_speed(lift_speed)

            if lift_speed != 0:
                lift.spin(FORWARD, lift_speed, PERCENT)
            else:
                lift.stop(HOLD)
        else:
            lift.stop(HOLD) # waiting for calibration

        # ---- Claw (calibration drives it while that runs) ----
        l1_pressed = controller_1.buttonL1.pressing()
        if not calibration.active:
            if l1_pressed and not l1_was_pressed:
                claw.toggle(now)
            claw.update(now, controller_1.buttonR1.pressing(), controller_1.buttonR2.pressing())
        l1_was_pressed = l1_pressed

        # ---- X: test the selected autonomous ----
        # Only without a field or competition switch, so it can't start by
        # accident in a match. Driving pauses until the test ends.
        x_pressed = controller_1.buttonX.pressing()
        if x_pressed and not x_was_pressed and not match_control_connected():
            run_auton_test()
            straight_active = False
            last_time = brain.timer.time(MSEC)
            x_pressed = False
        x_was_pressed = x_pressed

        wait(20, MSEC)


# ----------------------------------------------------------------------
# Startup intro
# The ICT Robotics logo wipes in along a 45° line, the same angle as the
# cuts in the logo. The controller only shows text, so it gets a text
# version of the same wipe, with "/" as the moving edge.
# ----------------------------------------------------------------------

LOGO_RED_COLOR = Color(152, 0, 0) # #980000, the band red
LOGO_FRAME_MS = 40 # time per animation frame


def draw_logo(reveal):
    # Draws the part of the logo left of the diagonal x + y = reveal
    # (in logo pixels). reveal >= LOGO_W + LOGO_H draws all of it.
    # The logo is stored as horizontal runs: y, start x, end x.
    brain.screen.set_pen_width(1)
    for color, runs in ((LOGO_RED_COLOR, LOGO_RED), (Color.WHITE, LOGO_WHITE)):
        brain.screen.set_pen_color(color)
        for i in range(0, len(runs), 3):
            y = runs[i]
            x0 = runs[i + 1]
            x1 = min(runs[i + 2], reveal - y)
            if x1 >= x0:
                brain.screen.draw_line(LOGO_X + x0, LOGO_Y + y, LOGO_X + x1, LOGO_Y + y)


def draw_wipe_edge(reveal):
    # Red diagonal line at the front of the wipe, clipped to the logo area.
    y0 = max(0, reveal - LOGO_W)
    y1 = min(LOGO_H, reveal)
    if y1 > y0:
        brain.screen.set_pen_width(3)
        brain.screen.set_pen_color(LOGO_RED_COLOR)
        brain.screen.draw_line(LOGO_X + reveal - y0, LOGO_Y + y0,
                               LOGO_X + reveal - y1, LOGO_Y + y1)
        brain.screen.set_pen_width(1)


# The controller screen is text only (3 rows x 19 columns), so it gets a
# text version of the logo with the same diagonal wipe. Each row is 19 characters.
CONTROLLER_LOGO = (
    "       I C T       ",
    "/ R O B O T I C S /",
)
CONTROLLER_COLUMNS = 19
CONTROLLER_SLANT = 2 # columns per row, characters are about twice as tall as wide
CONTROLLER_FRAME_EVERY = 2 # update it every 2nd Brain frame, its screen updates slowly


def controller_logo_rows(progress):
    # Text rows for wipe progress 0..1. Each row shows its text up to the wipe
    # edge, marked with "/". Upper rows are ahead, so the edge leans like
    # the cuts in the logo.
    extra = CONTROLLER_SLANT * (len(CONTROLLER_LOGO) - 1)
    edge = int(progress * (CONTROLLER_COLUMNS + extra))
    rows = []
    for row in range(len(CONTROLLER_LOGO)): # VEX Python has no enumerate()
        text = CONTROLLER_LOGO[row]
        end = edge - CONTROLLER_SLANT * row
        shown = text[:max(0, end)]
        if 0 <= end < CONTROLLER_COLUMNS:
            shown += "/"
        rows.append(shown + " " * (CONTROLLER_COLUMNS - len(shown)))
    return rows


def show_controller_logo(progress):
    rows = controller_logo_rows(progress)
    for row in range(len(rows)):
        controller_1.screen.set_cursor(row + 1, 1)
        controller_1.screen.print(rows[row])


def startup_intro():
    controller_1.screen.clear_screen()

    full = LOGO_W + LOGO_H # reveal value that shows the whole logo
    frames = max(1, INTRO_WIPE_MS // LOGO_FRAME_MS)
    for frame in range(frames + 1):
        reveal = full * frame // frames
        brain.screen.clear_screen(Color.BLACK)
        draw_logo(reveal)
        if frame < frames:
            draw_wipe_edge(reveal)
        brain.screen.render()

        if frame % CONTROLLER_FRAME_EVERY == 0 or frame == frames:
            show_controller_logo(frame / frames)
        wait(LOGO_FRAME_MS, MSEC)

    controller_1.screen.set_cursor(3, 1)
    controller_1.screen.print("  starting up...")

    wait(INTRO_HOLD_MS, MSEC)

    # Back to normal text drawing for the status screen
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_pen_color(Color.WHITE)
    controller_1.screen.clear_screen()


# ----------------------------------------------------------------------
# Startup logo data
# Generated by make_logo.py from the ICT Robotics logo, don't edit by hand.
# Each run is three numbers: y, start x, end x (in logo pixels).
# ----------------------------------------------------------------------

LOGO_W = 272
LOGO_H = 190
LOGO_X = 104 # centred on the 480 px wide screen
LOGO_Y = 12
LOGO_WHITE = (
    8, 113, 169, 8, 184, 262, 9, 42, 42, 9, 106, 168, 9, 183, 261, 10, 41, 42, 10, 102, 167, 10, 182, 260,
    11, 40, 42, 11, 98, 166, 11, 181, 259, 12, 39, 42, 12, 96, 165, 12, 180, 258, 13, 38, 42, 13, 93, 164,
    13, 179, 257, 14, 37, 42, 14, 91, 163, 14, 178, 256, 15, 36, 42, 15, 89, 162, 15, 177, 255, 16, 35, 42,
    16, 87, 161, 16, 176, 254, 17, 34, 42, 17, 85, 160, 17, 175, 253, 18, 33, 42, 18, 84, 159, 18, 174, 252,
    19, 32, 42, 19, 82, 158, 19, 173, 251, 20, 31, 42, 20, 80, 157, 20, 172, 250, 21, 30, 42, 21, 79, 156,
    21, 171, 249, 22, 29, 42, 22, 78, 155, 22, 170, 248, 23, 28, 42, 23, 77, 154, 23, 169, 247, 24, 27, 42,
    24, 75, 153, 24, 168, 246, 25, 26, 42, 25, 74, 152, 25, 167, 245, 26, 25, 42, 26, 73, 151, 26, 166, 244,
    27, 24, 42, 27, 72, 150, 27, 165, 243, 28, 23, 42, 28, 71, 149, 28, 164, 242, 29, 22, 42, 29, 70, 148,
    29, 163, 241, 30, 21, 42, 30, 69, 147, 30, 162, 240, 31, 20, 42, 31, 68, 146, 31, 161, 239, 32, 19, 42,
    32, 67, 145, 32, 160, 238, 33, 18, 42, 33, 66, 144, 33, 159, 237, 34, 17, 42, 34, 65, 143, 34, 158, 236,
    35, 16, 42, 35, 65, 142, 35, 157, 235, 36, 15, 42, 36, 64, 141, 36, 156, 234, 37, 14, 42, 37, 63, 140,
    37, 155, 233, 38, 13, 42, 38, 62, 139, 38, 154, 232, 39, 12, 42, 39, 62, 138, 39, 153, 231, 40, 11, 42,
    40, 61, 137, 40, 152, 230, 41, 10, 42, 41, 60, 116, 41, 183, 218, 42, 9, 42, 42, 60, 110, 42, 184, 218,
    43, 8, 42, 43, 59, 107, 43, 184, 218, 44, 8, 42, 44, 59, 104, 44, 184, 218, 45, 8, 42, 45, 58, 102,
    45, 184, 218, 46, 8, 42, 46, 58, 100, 46, 184, 218, 47, 8, 42, 47, 57, 99, 47, 184, 218, 48, 8, 42,
    48, 57, 97, 48, 184, 218, 49, 8, 42, 49, 56, 96, 49, 184, 218, 50, 8, 42, 50, 56, 95, 50, 184, 218,
    51, 8, 42, 51, 55, 94, 51, 184, 218, 52, 8, 42, 52, 55, 93, 52, 184, 218, 53, 8, 42, 53, 55, 92,
    53, 184, 218, 54, 8, 42, 54, 54, 91, 54, 184, 218, 55, 8, 42, 55, 54, 90, 55, 184, 218, 56, 8, 42,
    56, 54, 90, 56, 184, 218, 57, 8, 42, 57, 53, 89, 57, 184, 218, 58, 8, 42, 58, 53, 88, 58, 184, 218,
    59, 8, 42, 59, 53, 88, 59, 184, 218, 60, 8, 42, 60, 53, 87, 60, 184, 218, 61, 8, 42, 61, 53, 87,
    61, 184, 218, 62, 8, 42, 62, 52, 87, 62, 184, 218, 63, 8, 42, 63, 52, 86, 63, 184, 218, 64, 8, 42,
    64, 52, 86, 64, 184, 218, 65, 8, 42, 65, 52, 86, 65, 184, 218, 66, 8, 42, 66, 52, 85, 66, 184, 218,
    67, 8, 42, 67, 52, 85, 67, 184, 218, 68, 8, 42, 68, 52, 85, 68, 184, 218, 69, 8, 42, 69, 52, 85,
    69, 184, 218, 70, 8, 42, 70, 51, 85, 70, 184, 218, 71, 8, 42, 71, 51, 85, 71, 184, 218, 72, 8, 42,
    72, 51, 85, 72, 184, 218, 73, 8, 42, 73, 51, 84, 73, 184, 218, 74, 8, 42, 74, 51, 85, 74, 184, 218,
    75, 8, 42, 75, 51, 85, 75, 184, 218, 76, 8, 42, 76, 51, 85, 76, 184, 218, 77, 8, 42, 77, 52, 85,
    77, 184, 218, 78, 8, 42, 78, 52, 85, 78, 184, 218, 79, 8, 42, 79, 52, 85, 79, 184, 218, 80, 8, 42,
    80, 52, 85, 80, 184, 218, 81, 8, 42, 81, 52, 85, 81, 184, 218, 82, 8, 42, 82, 52, 86, 82, 184, 218,
    83, 8, 42, 83, 52, 86, 83, 184, 218, 84, 8, 42, 84, 52, 86, 84, 184, 218, 85, 8, 42, 85, 52, 87,
    85, 184, 218, 86, 8, 42, 86, 52, 87, 86, 184, 218, 87, 8, 42, 87, 53, 88, 87, 184, 218, 88, 8, 42,
    88, 53, 88, 88, 184, 218, 89, 8, 42, 89, 53, 89, 89, 184, 218, 90, 8, 42, 90, 53, 89, 90, 184, 218,
    91, 8, 42, 91, 54, 90, 91, 184, 218, 92, 8, 42, 92, 54, 91, 92, 184, 218, 93, 8, 42, 93, 54, 91,
    93, 184, 218, 94, 8, 42, 94, 54, 92, 94, 184, 218, 95, 8, 42, 95, 55, 93, 95, 184, 218, 96, 8, 42,
    96, 55, 94, 96, 184, 218, 97, 8, 42, 97, 56, 95, 97, 184, 218, 98, 8, 42, 98, 56, 96, 98, 184, 218,
    99, 8, 42, 99, 56, 98, 99, 184, 218, 100, 8, 42, 100, 57, 99, 100, 184, 218, 101, 8, 42, 101, 57, 101,
    101, 184, 218, 102, 8, 42, 102, 58, 103, 102, 184, 218, 103, 8, 42, 103, 58, 106, 103, 184, 218, 104, 8, 42,
    104, 59, 113, 104, 184, 218, 105, 8, 42, 105, 59, 128, 105, 184, 218, 106, 8, 42, 106, 60, 128, 106, 184, 218,
    107, 8, 42, 107, 61, 128, 107, 184, 218, 108, 8, 42, 108, 61, 128, 108, 184, 218, 109, 8, 42, 109, 62, 128,
    109, 184, 218, 110, 8, 42, 110, 62, 128, 110, 184, 218, 111, 8, 42, 111, 63, 128, 111, 184, 218, 112, 8, 42,
    112, 64, 128, 112, 184, 218, 113, 8, 42, 113, 65, 128, 113, 184, 218, 114, 8, 42, 114, 65, 128, 114, 184, 218,
    115, 8, 42, 115, 66, 128, 115, 184, 218, 116, 8, 42, 116, 67, 128, 116, 184, 218, 117, 8, 42, 117, 68, 128,
    117, 184, 218, 118, 8, 42, 118, 69, 128, 118, 184, 218, 119, 8, 42, 119, 70, 128, 119, 184, 218, 120, 8, 42,
    120, 71, 128, 120, 184, 218, 121, 8, 42, 121, 72, 128, 121, 184, 218, 122, 8, 42, 122, 73, 128, 122, 184, 218,
    123, 8, 42, 123, 74, 128, 123, 184, 218, 124, 8, 42, 124, 75, 128, 124, 184, 218, 125, 8, 42, 125, 77, 128,
    125, 184, 218, 126, 8, 42, 126, 78, 128, 126, 184, 218, 127, 8, 42, 127, 80, 128, 127, 184, 218, 128, 8, 42,
    128, 81, 128, 128, 184, 218, 129, 8, 42, 129, 83, 128, 129, 184, 218, 130, 8, 42, 130, 85, 128, 130, 184, 218,
    131, 8, 42, 131, 87, 128, 131, 184, 218, 132, 8, 42, 132, 89, 128, 132, 184, 218, 133, 8, 42, 133, 91, 128,
    133, 184, 218, 134, 8, 42, 134, 94, 128, 134, 184, 218, 135, 8, 42, 135, 98, 128, 135, 184, 218, 136, 8, 42,
    136, 104, 128, 136, 184, 218, 156, 43, 52, 156, 73, 79, 156, 96, 105, 156, 125, 131, 156, 147, 161, 156, 172, 175,
    156, 192, 198, 156, 218, 224, 157, 43, 54, 157, 71, 80, 157, 96, 106, 157, 123, 133, 157, 147, 161, 157, 172, 175,
    157, 191, 200, 157, 216, 225, 158, 43, 55, 158, 70, 81, 158, 96, 107, 158, 122, 134, 158, 147, 161, 158, 172, 175,
    158, 189, 201, 158, 215, 226, 159, 43, 56, 159, 69, 82, 159, 96, 99, 159, 103, 108, 159, 121, 134, 159, 147, 161,
    159, 172, 175, 159, 189, 202, 159, 215, 219, 159, 223, 227, 160, 43, 46, 160, 53, 56, 160, 69, 72, 160, 79, 83,
    160, 96, 98, 160, 105, 108, 160, 121, 125, 160, 131, 135, 160, 152, 155, 160, 172, 175, 160, 188, 192, 160, 199, 202,
    160, 214, 218, 160, 224, 227, 161, 43, 46, 161, 53, 56, 161, 68, 72, 161, 80, 83, 161, 96, 98, 161, 105, 108,
    161, 120, 124, 161, 132, 136, 161, 152, 155, 161, 172, 175, 161, 188, 191, 161, 199, 203, 161, 214, 217, 161, 224, 227,
    162, 43, 46, 162, 53, 56, 162, 68, 71, 162, 80, 84, 162, 96, 98, 162, 105, 108, 162, 120, 123, 162, 133, 136,
    162, 152, 155, 162, 172, 175, 162, 187, 191, 162, 200, 203, 162, 214, 218, 163, 43, 46, 163, 53, 56, 163, 68, 71,
    163, 81, 84, 163, 96, 99, 163, 104, 107, 163, 120, 123, 163, 133, 136, 163, 152, 155, 163, 172, 175, 163, 187, 190,
    163, 215, 221, 164, 43, 46, 164, 52, 56, 164, 68, 71, 164, 81, 84, 164, 96, 106, 164, 120, 123, 164, 133, 136,
    164, 152, 155, 164, 172, 175, 164, 187, 190, 164, 215, 224, 165, 43, 55, 165, 68, 71, 165, 81, 84, 165, 96, 107,
    165, 120, 123, 165, 133, 136, 165, 152, 155, 165, 172, 175, 165, 187, 190, 165, 217, 226, 166, 43, 55, 166, 68, 71,
    166, 81, 84, 166, 96, 108, 166, 120, 123, 166, 133, 136, 166, 152, 155, 166, 172, 175, 166, 187, 190, 166, 219, 227,
    167, 43, 53, 167, 68, 71, 167, 81, 84, 167, 96, 98, 167, 105, 109, 167, 120, 123, 167, 133, 136, 167, 152, 155,
    167, 172, 175, 167, 187, 190, 167, 223, 227, 168, 43, 46, 168, 50, 54, 168, 68, 71, 168, 80, 84, 168, 96, 98,
    168, 106, 109, 168, 120, 123, 168, 133, 136, 168, 152, 155, 168, 172, 175, 168, 187, 191, 168, 200, 203, 168, 214, 217,
    168, 224, 228, 169, 43, 46, 169, 51, 54, 169, 68, 72, 169, 80, 83, 169, 96, 98, 169, 106, 109, 169, 120, 124,
    169, 132, 135, 169, 152, 155, 169, 172, 175, 169, 188, 191, 169, 199, 202, 169, 214, 217, 169, 225, 228, 170, 43, 46,
    170, 51, 55, 170, 69, 73, 170, 79, 83, 170, 96, 98, 170, 105, 109, 170, 121, 125, 170, 131, 135, 170, 152, 155,
    170, 172, 175, 170, 188, 192, 170, 198, 202, 170, 214, 218, 170, 224, 228, 171, 43, 46, 171, 52, 55, 171, 69, 82,
    171, 96, 108, 171, 122, 134, 171, 152, 155, 171, 172, 175, 171, 189, 202, 171, 215, 227, 172, 43, 46, 172, 52, 56,
    172, 70, 81, 172, 96, 108, 172, 122, 133, 172, 152, 155, 172, 172, 175, 172, 190, 201, 172, 215, 227, 173, 43, 46,
    173, 53, 56, 173, 71, 80, 173, 96, 107, 173, 124, 132, 173, 152, 155, 173, 172, 175, 173, 191, 199, 173, 216, 225,
    174, 44, 46, 174, 54, 56, 174, 74, 78, 174, 96, 104, 174, 126, 130, 174, 153, 155, 174, 173, 175, 174, 193, 197,
    174, 218, 223,
)
LOGO_RED = (
    149, 40, 262, 150, 39, 261, 151, 38, 260, 152, 37, 259, 153, 36, 258, 154, 35, 257, 155, 34, 256, 156, 33, 42,
    156, 53, 72, 156, 80, 95, 156, 106, 124, 156, 132, 146, 156, 162, 171, 156, 176, 191, 156, 199, 217, 156, 225, 255,
    157, 32, 42, 157, 55, 70, 157, 81, 94, 157, 107, 122, 157, 134, 146, 157, 162, 171, 157, 176, 190, 157, 201, 215,
    157, 226, 254, 158, 31, 42, 158, 56, 69, 158, 82, 94, 158, 108, 121, 158, 135, 146, 158, 162, 171, 158, 176, 188,
    158, 202, 214, 158, 227, 253, 159, 30, 42, 159, 57, 68, 159, 83, 94, 159, 100, 102, 159, 109, 120, 159, 135, 146,
    159, 162, 171, 159, 176, 188, 159, 203, 214, 159, 220, 222, 159, 228, 252, 160, 29, 42, 160, 47, 52, 160, 57, 68,
    160, 73, 78, 160, 84, 94, 160, 100, 104, 160, 109, 120, 160, 126, 130, 160, 136, 151, 160, 157, 171, 160, 176, 187,
    160, 193, 198, 160, 203, 213, 160, 219, 223, 160, 228, 251, 161, 28, 42, 161, 47, 52, 161, 57, 67, 161, 73, 79,
    161, 84, 94, 161, 100, 104, 161, 109, 119, 161, 125, 131, 161, 137, 151, 161, 157, 171, 161, 176, 187, 161, 192, 198,
    161, 204, 213, 161, 218, 223, 161, 228, 250, 162, 27, 42, 162, 47, 52, 162, 57, 67, 162, 72, 79, 162, 85, 94,
    162, 100, 104, 162, 109, 119, 162, 124, 132, 162, 137, 151, 162, 157, 171, 162, 176, 186, 162, 192, 199, 162, 204, 213,
    162, 219, 249, 163, 26, 42, 163, 47, 52, 163, 57, 67, 163, 72, 80, 163, 85, 94, 163, 100, 103, 163, 108, 119,
    163, 124, 132, 163, 137, 151, 163, 157, 171, 163, 176, 186, 163, 191, 214, 163, 222, 248, 164, 25, 42, 164, 47, 51,
    164, 57, 67, 164, 72, 80, 164, 85, 94, 164, 107, 119, 164, 124, 132, 164, 137, 151, 164, 157, 171, 164, 176, 186,
    164, 191, 214, 164, 225, 247, 165, 24, 42, 165, 56, 67, 165, 72, 80, 165, 85, 94, 165, 108, 119, 165, 124, 132,
    165, 137, 151, 165, 157, 171, 165, 176, 186, 165, 191, 216, 165, 227, 246, 166, 23, 42, 166, 56, 67, 166, 72, 80,
    166, 85, 94, 166, 109, 119, 166, 124, 132, 166, 137, 151, 166, 157, 171, 166, 176, 186, 166, 191, 218, 166, 228, 245,
    167, 22, 42, 167, 54, 67, 167, 72, 80, 167, 85, 94, 167, 100, 104, 167, 110, 119, 167, 124, 132, 167, 137, 151,
    167, 157, 171, 167, 176, 186, 167, 191, 222, 167, 228, 244, 168, 21, 42, 168, 47, 49, 168, 55, 67, 168, 72, 79,
    168, 85, 94, 168, 100, 105, 168, 110, 119, 168, 124, 131, 168, 137, 151, 168, 157, 171, 168, 176, 186, 168, 192, 199,
    168, 204, 213, 168, 218, 223, 168, 229, 243, 169, 20, 42, 169, 47, 50, 169, 55, 67, 169, 73, 79, 169, 84, 94,
    169, 100, 105, 169, 110, 119, 169, 125, 131, 169, 136, 151, 169, 157, 171, 169, 176, 187, 169, 192, 198, 169, 203, 213,
    169, 218, 224, 169, 229, 242, 170, 19, 42, 170, 47, 50, 170, 56, 68, 170, 74, 78, 170, 84, 94, 170, 100, 104,
    170, 110, 120, 170, 126, 130, 170, 136, 151, 170, 157, 171, 170, 176, 187, 170, 193, 197, 170, 203, 213, 170, 219, 223,
    170, 229, 241, 171, 18, 42, 171, 47, 51, 171, 56, 68, 171, 83, 94, 171, 109, 121, 171, 135, 151, 171, 157, 171,
    171, 176, 188, 171, 203, 214, 171, 228, 240, 172, 17, 42, 172, 47, 51, 172, 57, 69, 172, 82, 94, 172, 109, 121,
    172, 134, 151, 172, 157, 171, 172, 176, 189, 172, 202, 214, 172, 228, 239, 173, 16, 42, 173, 47, 52, 173, 57, 70,
    173, 81, 94, 173, 108, 123, 173, 133, 151, 173, 157, 171, 173, 176, 190, 173, 200, 215, 173, 226, 238, 174, 15, 43,
    174, 47, 53, 174, 57, 73, 174, 79, 95, 174, 105, 125, 174, 131, 152, 174, 156, 172, 174, 176, 192, 174, 198, 217,
    174, 224, 237, 175, 14, 236, 176, 13, 235, 177, 12, 234, 178, 11, 233, 179, 10, 232, 180, 9, 231, 181, 8, 230,
)


# ----------------------------------------------------------------------
# Status display (Brain and controller screens)
# ----------------------------------------------------------------------

def controller_rows(battery, lift_deg, alerts, hot):
    # The three controller rows. Until the lift is calibrated, the whole
    # screen is the calibration prompt.
    auton_name = AUTONS[selected_auton][0]
    if auton_test_running:
        rows = ["AUTO TEST", auton_name, "X = stop"]
    elif lift_status == "not calibrated":
        if robot_enabled():
            rows = ["CALIBRATION", "Lift + claw move!", "Press B to start"]
        else:
            # Waiting for the match: show which autonomous will run
            rows = ["Auto: " + auton_name, "Robot disabled,", "lift cal at start"]
    elif lift_status == "calibrating":
        rows = ["CALIBRATION", "Calibrating...", "Keep hands clear"]
    elif lift_status == "failed":
        rows = ["LIFT CAL FAILED", "Check the lift,", "then press B"]
    else:
        if hot:
            second = "MOTORS HOT"
        elif controller_1.buttonL2.pressing():
            second = "LIFT LIMITS OFF"
        else:
            second = "Claw " + claw.state_text()
        if brain.timer.time(MSEC) - lift_ready_at < 3000:
            third = "READY"
        elif not match_control_connected():
            third = "X test: " + auton_name # practice: what X will run
        else:
            third = ""
        rows = ["Bat " + str(battery) + "%  Lift " + str(lift_deg), second, third]

    if alerts:
        rows[0] = "NO " + alerts[0] + " A=ok" # an unplugged device beats everything
    for i in range(len(rows)):
        rows[i] = rows[i][:19] # controller rows are 19 characters wide
    return rows


def show_controller_rows(rows, old_rows):
    # Writes the rows to the controller, skipping rows that haven't changed.
    # The controller screen is slow over radio, so fewer writes is better.
    for i in range(len(rows)):
        if old_rows[i] != rows[i]:
            controller_1.screen.clear_row(i + 1)
            controller_1.screen.set_cursor(i + 1, 1)
            controller_1.screen.print(rows[i])


def unplugged_devices():
    # Names of devices the Brain can't see right now.
    missing = []
    for name, device in DEVICES:
        try:
            if not device.installed():
                missing.append(name)
        except Exception:
            pass # device type without installed(), skip it
    return missing


# Missing devices the driver has OK'd with A. They're still listed on the
# Brain screen, but don't warn on the controller or rumble.
acknowledged = []


def acknowledge_missing():
    # Controller A: OK everything that's missing right now, e.g. a vision
    # sensor that isn't mounted yet. If a device comes back and then goes
    # missing again later, it warns again.
    for name in unplugged_devices():
        if name not in acknowledged:
            acknowledged.append(name)


def missing_alerts(missing):
    # Missing devices that still need a warning.
    for name in acknowledged[:]:
        if name not in missing:
            acknowledged.remove(name) # it's back, so warn if it goes missing again
    return [name for name in missing if name not in acknowledged]


def status_loop():
    if STARTUP_INTRO:
        try:
            startup_intro()
        except Exception as error:
            # A broken intro must never take the status screens down with it
            print("startup intro failed:", error)
            brain.screen.set_font(FontType.MONO20)
            controller_1.screen.clear_screen()

    known_alerts = []
    shown_rows = [None, None, None] # what the controller shows now

    while True:
        missing = unplugged_devices()
        alerts = missing_alerts(missing)
        if any(name not in known_alerts for name in alerts):
            controller_1.rumble("---") # something new came unplugged
        known_alerts = alerts

        lift_deg = int(lift.position(DEGREES))
        lift_temp = max(int(m.temperature(TemperatureUnits.CELSIUS)) for m in lift_motors)
        drive_temp = max(int(left_drive.temperature(TemperatureUnits.CELSIUS)),
                         int(right_drive.temperature(TemperatureUnits.CELSIUS)))
        claw_temp = int(claw_motor.temperature(TemperatureUnits.CELSIUS))
        battery = int(brain.battery.capacity())
        target = find_target()
        hot = max(lift_temp, drive_temp, claw_temp) >= HOT_TEMP_C

        # Brain screen
        brain.screen.clear_screen()
        brain.screen.set_cursor(1, 1)
        if lift_status == "not calibrated":
            brain.screen.set_pen_color(Color.YELLOW)
            if robot_enabled():
                brain.screen.print("Press B on the controller to calibrate.")
                brain.screen.next_row()
                brain.screen.print("Keep hands away, the claw and lift will move.")
            else:
                brain.screen.print("Robot disabled. The lift calibrates when the match starts.")
            brain.screen.set_pen_color(Color.WHITE)
        elif lift_status == "calibrating":
            brain.screen.set_pen_color(Color.YELLOW)
            brain.screen.print("Calibrating claw and lift...")
            brain.screen.set_pen_color(Color.WHITE)
        elif lift_status == "failed":
            brain.screen.set_pen_color(Color.RED)
            brain.screen.print("Lift calibration failed. Check the lift, then press B.")
            brain.screen.set_pen_color(Color.WHITE)
        elif lift_status == "assumed":
            brain.screen.set_pen_color(Color.GREEN)
            brain.screen.print("Lift zero = start position. B = full calibration.")
            brain.screen.set_pen_color(Color.WHITE)
        else:
            brain.screen.set_pen_color(Color.GREEN)
            brain.screen.print("Calibrated - READY")
            brain.screen.set_pen_color(Color.WHITE)
        brain.screen.next_row()
        if claw_status == "failed":
            brain.screen.set_pen_color(Color.RED)
            brain.screen.print("Claw calibration failed: it opens on a timer instead.")
            brain.screen.set_pen_color(Color.WHITE)
        brain.screen.next_row()

        brain.screen.set_pen_color(Color.CYAN)
        brain.screen.print("Auto: " + AUTONS[selected_auton][0] + "  (tap screen to change)")
        brain.screen.set_pen_color(Color.WHITE)
        brain.screen.next_row()
        brain.screen.print("Lift: " + str(lift_deg) + " deg (max " + str(LIFT_MAX_DEG) + ")")
        brain.screen.next_row()
        claw_text = "Claw: " + claw.state_text() + ", at " + str(int(claw_motor.position(DEGREES))) + " deg"
        if claw_closed_deg is not None:
            claw_text += " (closes empty at " + str(int(claw_closed_deg)) + ")"
        brain.screen.print(claw_text)
        brain.screen.next_row()
        brain.screen.print("Drive speed " + str(int(lift_drive_scale() * 100))
                           + " %  wheel diff " + str(int(wheel_difference())))
        brain.screen.next_row()
        brain.screen.print("Temp C  drive " + str(drive_temp) + "  lift " + str(lift_temp)
                           + "  claw " + str(claw_temp))
        brain.screen.next_row()
        brain.screen.print("Battery: " + str(battery) + " %")
        brain.screen.next_row()
        if "VISION" in missing:
            brain.screen.print("Vision: not connected")
        elif target is not None:
            brain.screen.print("Vision: id " + str(target.id) + "  err "
                               + str(target.centerX - SENSOR_CENTER_X)
                               + "  h " + str(target.height))
        else:
            brain.screen.print("Vision: nothing")
        brain.screen.next_row()
        if alerts:
            brain.screen.set_pen_color(Color.RED)
            brain.screen.print("UNPLUGGED: " + ", ".join(alerts) + " (A on controller = OK)")
            brain.screen.set_pen_color(Color.WHITE)
            brain.screen.next_row()
        if acknowledged:
            brain.screen.set_pen_color(Color(128, 128, 128))
            brain.screen.print("Missing, OK'd: " + ", ".join(acknowledged))
            brain.screen.set_pen_color(Color.WHITE)
        brain.screen.render() # show the whole frame at once, no flicker

        # Controller screen
        rows = controller_rows(battery, lift_deg, alerts, hot)
        show_controller_rows(rows, shown_rows)
        shown_rows = rows

        wait(250, MSEC)


# ----------------------------------------------------------------------
# Startup
# Nothing moves here. The lift waits for B (or for autonomous to start).
# ----------------------------------------------------------------------

def pre_autonomous():
    left_drive.set_stopping(BRAKE)
    right_drive.set_stopping(BRAKE)

    lift.set_stopping(HOLD)
    lift.set_position(0, DEGREES) # temporary, replaced by calibration

    claw_motor.set_stopping(HOLD)
    claw_motor.set_max_torque(CLAW_TORQUE, PERCENT)


competition = Competition(user_control, autonomous)
pre_autonomous()
controller_1.buttonA.pressed(acknowledge_missing)
brain.screen.pressed(next_auton)
status_thread = Thread(status_loop)
