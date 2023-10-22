@if (@X)==(@Y) @end /* JScript comment 
        @echo off 
       
        rem :: the first argument is the script name as it will be used for proper help message 
        cscript //E:JScript //nologo "%~f0" "%~nx0" %* 
        exit /b %errorlevel% 
@if (@X)==(@Y) @end JScript comment */ 


var sh=new ActiveXObject("WScript.Shell"); 
var ARGS = WScript.Arguments; 
var scriptName=ARGS.Item(0); 

var title="";
var timestep="";

function printHelp(){ 
        WScript.Echo(scriptName + " - resumes Command after each time it is paused"); 
        WScript.Echo("Usage:"); 
        WScript.Echo("call " + scriptName + " title timestep"); 
        WScript.Echo("title  - the title of the application");
        WScript.Echo("timestep  - the number of seconds to sleep before resuming the simulation");  
} 

function parseArgs(){ 
        if (ARGS.Length < 3) { 
                WScript.Echo("insufficient arguments"); 
                printHelp(); 
                WScript.Quit(43); 
        }
		
		title=ARGS.Item(1);
                timestep=ARGS.Item(2);
}

parseArgs();

if (title === "") {
	WScript.Quit(0);
}

// focus on the application and start running the scenario
sh.AppActivate(title)
sh.SendKeys("{ }");

// the scenario will be paused every X seconds, so resume the game every X+1 seconds by sending the ENTER key command
while (true) {
  WScript.Sleep(timestep * 1000);
  sh.AppActivate(title);
  sh.SendKeys("{ENTER}");
}

WScript.Quit(0);