from machine import Pin
from hx711 import HX711
from motor import Motor
import utime

'''
-----------------------------
      Open/Closed Switch
-----------------------------
'''
# Set the limit pin high by default, NO (Disconnects when in contact)
limitSwitch = Pin(1, Pin.IN, Pin.PULL_UP)

'''
-----------------------------
      Spring Actuators
-----------------------------
'''
actuators = Motor(Pin(18, Pin.OUT), Pin(19, Pin.OUT))

'''
-----------------------------
          Loadcell
-----------------------------
'''
loadcell = HX711(13, 12)
# Switch states
bOpen = 1
bClosed = 0

iLoadcellThreshold = loadcell.read() * 1.4
'''
-----------------------------
        Stepper motor
-----------------------------
'''

# Stepper motor driver
step = Pin(14)
direction = Pin(15, Pin.OUT)

# To control speed just modify the amount/value of nop[dely amount 0-31].
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def move():
    wrap_target()
    set(pins, 1)   [31]
    nop()          [31]
    nop()          [31]
    set(pins, 0)   [31]
    nop()          [31]
    nop()          [31]
    wrap()

"""Instantiate a state machine with the move
program, at 100000Hz, with set base to step pin."""
stepper = rp2.StateMachine(0, move, freq=100000, set_base=step)
direction.value(0)
bLowered = 0

'''
-----------------------------
           States
-----------------------------
'''
eOFF = (0, "off")

eSTARTUP = (1, "Startup")
eSTARTUP_DECISION = (1, "Decision")
eSTARTUP_OPENING = (2, "Opening")

eUNLOADING = (2, "Unloading")
eUNLOADING_DECISION = (1, "Decision")
eUNLOADING_LOWERING = (2, "Lowering")
eUNLOADING_OPENING = (3, "Opening")
eUNLOADING_LIFTING = (4, "Lifting")

eUNLOADED = (3, "Unloaded")
eUNLOADED_DECISION = (1, "Decision")

eLOADING = (4, "Loading")
eLOADING_DECISION = (1, "Decision")
eLOADING_LOWERING = (2, "Lowering")
eLOADING_CLOSING = (3, "Closing")
eLOADING_LIFTING = (4, "Lifting")

eLOADED = (5, "Loaded")
eLOADED_DECISION = (1, "Decision")
eLOADED_TOUCHDOWN = (2, "Touch down")
eLOADED_TAKEOFF = (3, "Take off")

# Initializing the starting states and steps
iNextState = eSTARTUP
iState = eSTARTUP
iNextStep = eSTARTUP_DECISION
iStep = eSTARTUP_DECISION

# Set the beginning states to be the off state
iPrevStep = eOFF
iPrevState = eOFF

# Lifting time parameters
bLiftStart = 1
tLiftTime = 5000

# Toolhead raised state (Unloaded and loaded)
bLifted = 0
bLowered = 0

bTouchingSurface = 0

while True:
    
    # if the State or step has changed, output the new state
    if (iState != iPrevState) or (iStep != iPrevStep):
        print("\n")
        print("State: {}".format(iState[1]))
        print("Step: {}".format(iStep[1]))
    
    # Capture inputs
    bSwitchState = limitSwitch.value()
    iLoadcellReading = loadcell.read()
    
    # Startup state
    if iState == eSTARTUP:
        
        # Decision step
        if iStep == eSTARTUP_DECISION:
            if bSwitchState == bClosed:
                iNextStep = eSTARTUP_OPENING
            else:
                bLifted = 1
                iNextStep = eUNLOADED_DECISION
                iNextState = eUNLOADED
                
        # Opening Step
        if iStep == eSTARTUP_OPENING:
            actuators.speed(20)
            if bSwitchState == bOpen:
                actuators.speed(0)
                iNextStep = eSTARTUP_DECISION
                
    # Unloading state
    if iState == eUNLOADING:
        
        # Decision Step
        if iStep == eUNLOADING_DECISION:
            
            # If the atc is in this state it is done unloading 
            if bSwitchState == bOpen and bLifted:
                iNextState = eUNLOADED
                iNextStep = eUNLOADED_DECISION
            if bSwitchState == bOpen and bLowered:
                iNextStep = eUNLOADING_LIFTING
            if bSwitchState == bClosed and bLifted:
                iNextStep = eUNLOADING_LOWERING
            if bSwitchState == bClosed and bLowered:
                iNextStep = eUNLOADING_OPENING
                
        if iStep == eUNLOADING_LOWERING:
            stepper.active(1)
            if iLoadcellReading > iLoadcellThreshold:
                stepper.active(0)
                direction.value(1)
                bLifted = 0
                bLowered = 1
                iNextStep = eUNLOADING_DECISION
                
        if iStep == eUNLOADING_OPENING:
            actuators.speed(-20)
            if bSwitchState == bOpen:
                actuators.speed(0)
                iNextStep = eUNLOADING_DECISION
                
        if iStep == eUNLOADING_LIFTING:
            stepper.active(1)                   # Turn stepper motor on
            if bLiftStart:
                startTime = utime.ticks_ms()    # Get the ticks at the start of lifting
                bLiftStart = 0                  # Flip the lift start flag on
            if utime.ticks_diff(utime.ticks_ms(), startTime) > tLiftTime:
                stepper.active(0)               # Shut the stepper motor off
                bLiftStart = 1                  # Reset the lift start flag for next cycle
                bLifted = 1                     # Set the lifted flag for the toolhead
                bLowered = 0                    # Remove the lowered flag for the toolhead
                iNextStep = eUNLOADING_DECISION
    
    # Unloaded state
    if iState == eUNLOADED:
        utime.sleep(5)
        
        if iStep == eUNLOADED_DECISION:     
            if bLiftRequest and bLowered:
                stepper.active(1)                   # Turn stepper motor on
                if bLiftStart:
                    startTime = utime.ticks_ms()    # Get the ticks at the start of lifting
                    bLiftStart = 0                  # Flip the lift start flag on
                if utime.ticks_diff(utime.ticks_ms(), startTime) > tLiftTime:
                    stepper.active(0)               # Shut the stepper motor off
                    bLiftStart = 1                  # Reset the lift start flag for next cycle
                    bLifted = 1                     # Set the lifted flag for the toolhead
                    bLowered = 0                    # Remove the lowered flag for the toolhead
            else if bLowerRequest and bLifted:
                stepper.active(1)                   # Turn stepper motor on
                if bLiftStart:
                    startTime = utime.ticks_ms()    # Get the ticks at the start of lifting
                    bLiftStart = 0                  # Flip the lift start flag on
                if utime.ticks_diff(utime.ticks_ms(), startTime) > tLiftTime:
                    stepper.active(0)               # Shut the stepper motor off
                    bLiftStart = 1                  # Reset the lift start flag for next cycle
                    bLifted = 1                     # Set the lifted flag for the toolhead
                    bLowered = 0                    # Remove the lowered flag for the toolhead
                
            
        
        
        
        # if LoadingREQUEST: FIGURE OUT FROM 3DPRINTER
        iNextState = eLOADING
        iNextStep = eLOADING_DECISION
        
    # Loading state     
    if iState == eLOADING:
        
        # Decision step
        if iStep == eLOADING_DECISION:
            if bSwitchState == bClosed and bLifted:
                iNextState = eLOADED
                iNextStep = eLOADED_DECISION
            if bSwitchState == bClosed and bLowered:
                iNextStep = eLOADING_LIFTING
            if bSwitchState == bOpen and bLifted:
                iNextStep = eLOADING_LOWERING
            if bSwitchState == bOpen and bLowered:
                iNextStep = eLOADING_CLOSING
        
        # Lowering step
        if iStep == eLOADING_LOWERING:
            stepper.active(1)
            if iLoadcellReading > iLoadcellThreshold:
                stepper.active(0)
                direction.value(1)
                bLifted = 0
                bLowered = 1
                iNextStep = eLOADING_DECISION
        
        # Closing step
        if iStep == eLOADING_CLOSING:
            actuators.speed(-20)
            if bSwitchState == bClosed:
                actuators.speed(0)
                iNextStep = eLOADING_DECISION
                
        # Lifting step
        if iStep == eLOADING_LIFTING:
            stepper.active(1)
            if bLiftStart:
                startTime = utime.ticks_ms()
                bLiftStart = 0
            if utime.ticks_diff(utime.ticks_ms(), startTime) > tLiftTime:
                stepper.active(0)
                bLiftStart = 1
                bLifted = 1
                bLowered = 0
                iNextStep = eLOADING_DECISION
                
    # Loaded state:
    if iState == eLOADED:
        
        # Decision step
        if iStep == eLOADED_DECISION:
            utime.sleep(5)
            # if LoadingREQUEST: FIGURE OUT FROM 3DPRINTER
            iNextState = eUNLOADING
            iNextStep = eUNLOADING_DECISION
                
    # Set out the points
    iPrevState = iState
    iPrevStep  = iStep
    
    # Increment the states and steps
    iState = iNextState
    iStep = iNextStep
            
    
    
          
        

    