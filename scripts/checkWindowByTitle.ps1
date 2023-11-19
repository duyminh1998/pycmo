# https://superuser.com/questions/1328345/find-all-window-titles-of-application-through-command-line
Add-Type  @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;    
    public class Win32 {
        public delegate void ThreadDelegate(IntPtr hWnd, IntPtr lParam);
        
        [DllImport("user32.dll")]
        public static extern bool EnumThreadWindows(int dwThreadId, 
            ThreadDelegate lpfn, IntPtr lParam);
        
        [DllImport("user32.dll", CharSet=CharSet.Auto, SetLastError=true)]
        public static extern int GetWindowText(IntPtr hwnd, 
            StringBuilder lpString, int cch);
        
        [DllImport("user32.dll", CharSet=CharSet.Auto, SetLastError=true)]
        public static extern Int32 GetWindowTextLength(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool IsIconic(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);

        public static string GetTitle(IntPtr hWnd) {
            var len = GetWindowTextLength(hWnd);
            StringBuilder title = new StringBuilder(len + 1);
            GetWindowText(hWnd, title, title.Capacity);
            return title.ToString();
        }
    }
"@

$windows = New-Object System.Collections.ArrayList
Get-Process | Where { $_.MainWindowTitle } | foreach {
    $_.Threads.ForEach({
        [void][Win32]::EnumThreadWindows($_.Id, {
            param($hwnd, $lparam)
            if ([Win32]::IsIconic($hwnd) -or [Win32]::IsWindowVisible($hwnd)) {
                if ([Win32]::GetTitle($hwnd) -eq "Side selection and briefing") {
                    $windows.Add($true)
                }
            }}, 0)
        })}
Write-Output $windows