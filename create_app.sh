#!/bin/bash

# Create the Applications directory if it doesn't exist
mkdir -p "EEG Analysis.app/Contents/MacOS"
mkdir -p "EEG Analysis.app/Contents/Resources"

# Compile the AppleScript
osacompile -o "EEG Analysis.app/Contents/Resources/Scripts/main.scpt" EEG_Analysis.applescript

# Create the Info.plist file
cat > "EEG Analysis.app/Contents/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>applet</string>
    <key>CFBundleIconFile</key>
    <string>applet</string>
    <key>CFBundleIdentifier</key>
    <string>com.eeg.analysis</string>
    <key>CFBundleName</key>
    <string>EEG Analysis</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOL

# Copy the applet executable
cp /System/Library/CoreServices/Automator.app/Contents/MacOS/applet "EEG Analysis.app/Contents/MacOS/"

# Make the app executable
chmod +x "EEG Analysis.app/Contents/MacOS/applet"

echo "🎉 Application created successfully!"
echo "📱 You can now drag 'EEG Analysis.app' to your Dock" 