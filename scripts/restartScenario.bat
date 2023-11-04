@if (@X)==(@Y) @end /* JScript comment 
        @echo off 
       
        rem :: the first argument is the script name as it will be used for proper help message 
        cscript //E:JScript //nologo "%~f0" "%~nx0" %* 
        exit /b %errorlevel% 
@if (@X)==(@Y) @end JScript comment */ 


var sh=new ActiveXObject("WScript.Shell"); 

sh.AppActivate("Steam demo - Command v1.06 - Build 1328.11")
sh.SendKeys("%{1}"); 
sh.SendKeys("{ENTER}"); 
WScript.Sleep(500)
sh.SendKeys("{DOWN}"); 
sh.SendKeys("{DOWN}"); 
sh.SendKeys("{DOWN}"); 
WScript.Sleep(500)
sh.SendKeys("{RIGHT}"); 
WScript.Sleep(500)
sh.SendKeys("{ENTER}"); 
WScript.Sleep(3000)
sh.AppActivate("Side selection and briefing")
sh.SendKeys("{ESCAPE}"); 
WScript.Quit(0);