tell application "Terminal"
    -- Get the path to the script's directory
    set scriptPath to POSIX path of (path to me)
    set scriptDir to do shell script "dirname " & quoted form of scriptPath
    
    -- Activate Terminal
    activate
    
    -- Run the shell script
    do script "cd " & quoted form of scriptDir & " && ./run.sh"
end tell 