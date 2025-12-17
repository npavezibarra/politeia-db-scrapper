"""
Simple Mouse Wiggle Test
Run this to see if Python has permission to move your mouse.
"""
import pyautogui
import time
import sys

print("="*40)
print("MOUSE WIGGLE TEST")
print("="*40)
print("I will move your mouse in a square shape in 3 seconds.")
print("Please DO NOT touch the mouse.")
print("If the mouse does not move, you have a Permission Issue.")
print("\nReady? (Press Ctrl+C to cancel)")
try:
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
        
    print("\nAttempting to move mouse...")
    
    # Get current position
    x, y = pyautogui.position()
    print(f"Start Position: ({x}, {y})")
    
    # Move Right
    pyautogui.moveRel(100, 0, duration=0.5)
    print("Moved Right ->")
    
    # Move Down
    pyautogui.moveRel(0, 100, duration=0.5)
    print("Moved Down v")
    
    # Move Left
    pyautogui.moveRel(-100, 0, duration=0.5)
    print("Moved Left <-")
    
    # Move Up
    pyautogui.moveRel(0, -100, duration=0.5)
    print("Moved Up ^")
    
    print("\n✓ Test Complete!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("On macOS, you likely need to grant Accessibility permissions.")
    print("System Settings > Privacy & Security > Accessibility > Add 'Terminal' or 'VS Code'")
