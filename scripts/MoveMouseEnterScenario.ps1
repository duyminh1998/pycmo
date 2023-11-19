$cSource = @'
using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class Clicker
{
    // https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
    [StructLayout(LayoutKind.Sequential)]
    struct INPUT
    { 
        public int        type; // 0 = INPUT_MOUSE
        // 1 = INPUT_KEYBOARD
        // 2 = INPUT_HARDWARE
        public MOUSEINPUT mi;
}

// https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
[StructLayout(LayoutKind.Sequential)]
struct MOUSEINPUT
{
    public int    dx;
    public int    dy;
    public int    mouseData;
    public int    dwFlags;
    public int    time;
    public IntPtr dwExtraInfo;
}

// This covers most use cases although complex mice may have additional buttons.
// There are additional constants you can use for those cases, see the MSDN page.
const int MOUSEEVENTF_MOVE       = 0x0001;
const int MOUSEEVENTF_LEFTDOWN   = 0x0002;
const int MOUSEEVENTF_LEFTUP     = 0x0004;
const int MOUSEEVENTF_RIGHTDOWN  = 0x0008;
const int MOUSEEVENTF_RIGHTUP    = 0x0010;
const int MOUSEEVENTF_MIDDLEDOWN = 0x0020;
const int MOUSEEVENTF_MIDDLEUP   = 0x0040;
const int MOUSEEVENTF_WHEEL      = 0x0080;
const int MOUSEEVENTF_XDOWN      = 0x0100;
const int MOUSEEVENTF_XUP        = 0x0200;
const int MOUSEEVENTF_ABSOLUTE   = 0x8000;

const int screen_length = 0x10000;

// https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
[System.Runtime.InteropServices.DllImport("user32.dll")]
extern static uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

public static void LeftClickAtPoint(int x, int y)
{
    // Move the mouse
    INPUT[] input = new INPUT[3];
    
    input[0].mi.dx = x * (65535 / System.Windows.Forms.Screen.PrimaryScreen.Bounds.Width);
    input[0].mi.dy = y * (65535 / System.Windows.Forms.Screen.PrimaryScreen.Bounds.Height);
    input[0].mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE;
    
    // Left mouse button down
    input[1].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    
    // Left mouse button up
    input[2].mi.dwFlags = MOUSEEVENTF_LEFTUP;
    
    SendInput(3, input, Marshal.SizeOf(input[0]));
}
}
'@

$wshell = New-Object -ComObject wscript.shell;
$wshell.AppActivate('Side selection and briefing')
Start-Sleep -s 1
$wshell.SendKeys("%{ }"); 
$wshell.SendKeys("m");
Start-Sleep -s 1

$MOVEMENTSIZEY = 770
$MOVEMENTSIZEX = 600

Add-Type -AssemblyName System.Windows.Forms
$POSITION = [Windows.Forms.Cursor]::Position
$POSITION.y += $MOVEMENTSIZEY
$POSITION.x -= $MOVEMENTSIZEX

Add-Type -TypeDefinition $cSource -ReferencedAssemblies System.Windows.Forms,System.Drawing

# Send a click at a specified point
$wshell.SendKeys('{ESC}')
[Clicker]::LeftClickAtPoint($POSITION.x, $POSITION.y)
Start-Sleep -s 1