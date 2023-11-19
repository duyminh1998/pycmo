@if (@X)==(@Y) @end /* JScript comment 
        @echo off 
       
        rem :: the first argument is the script name as it will be used for proper help message 
        cscript //E:JScript //nologo "%~f0" "%~nx0" %* 
        exit /b %errorlevel% 
@if (@X)==(@Y) @end JScript comment */ 


var sh=new ActiveXObject("WScript.Shell"); 
var ARGS = WScript.Arguments; 
var scriptName=ARGS.Item(0); 

var title = "";
var loadDuration = "5000";

function printHelp(){ 
        WScript.Echo(scriptName + " - restarts a scenario in Command"); 
        WScript.Echo("Usage:"); 
        WScript.Echo("call " + scriptName + " title string"); 
        WScript.Echo("title  - the title of the application"); 
        WScript.Echo("loadDuration  - how long it takes for the scenario to load"); 
} 

function parseArgs(){ 
        if (ARGS.Length < 3) { 
                WScript.Echo("insufficient arguments"); 
                printHelp(); 
                WScript.Quit(43); 
        }
        title=ARGS.Item(1);
        loadDuration=ARGS.Item(2);
}

parseArgs();

sh.AppActivate(title)
WScript.Sleep(1000);
sh.SendKeys("%f");
WScript.Sleep(500);
sh.SendKeys("{DOWN}");
sh.SendKeys("{DOWN}");
sh.SendKeys("{DOWN}"); 
WScript.Sleep(1000)
sh.SendKeys("{RIGHT}"); 
WScript.Sleep(500)
sh.SendKeys("{ENTER}"); 
WScript.Sleep(loadDuration);
sh.AppActivate(title);
WScript.Quit(0);