@if (@X)==(@Y) @end /* JScript comment 
        @echo off 
       
        rem :: the first argument is the script name as it will be used for proper help message 
        cscript //E:JScript //nologo "%~f0" "%~nx0" %* 
        exit /b %errorlevel% 
@if (@X)==(@Y) @end JScript comment */ 


var sh=new ActiveXObject("WScript.Shell"); 
var ARGS = WScript.Arguments; 
var scriptName=ARGS.Item(0); 

var title = "Scenario End";

function printHelp(){ 
        WScript.Echo(scriptName + " - closes the message that pops up after ending a scenario in Command"); 
        WScript.Echo("Usage:"); 
        WScript.Echo("call " + scriptName); 
} 

sh.AppActivate(title)
WScript.Sleep(3000); 
sh.SendKeys("{ }"); 
WScript.Sleep(3000);
sh.SendKeys("{ESC}"); 
WScript.Quit(0);