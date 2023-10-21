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
var keys="";
var timestep = 17;

function printHelp(){ 
        WScript.Echo(scriptName + " - sends keys to a applicaion with given title"); 
        WScript.Echo("Usage:"); 
        WScript.Echo("call " + scriptName + " title string"); 
        WScript.Echo("title  - the title of the application"); 
} 

function parseArgs(){ 
                
        if (ARGS.Length < 2) { 
                WScript.Echo("insufficient arguments"); 
                printHelp(); 
                WScript.Quit(43); 
        }
		
		title=ARGS.Item(1);
}


function escapeRegExp(str) {
    return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
}

parseArgs();

if (title === "") {
	sh.SendKeys(keys); 
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