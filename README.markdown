Generate installs key for Munki pkginfo files given an installer package. Example:

    # ./extractinstalls.py /Volumes/Command\ Line\ Tools\ \(Mountain\ Lion\)/Command\ Line\ Tools\ \(Mountain\ Lion\).mpkg
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>installs</key>
        <array>
            <dict>
                <key>CFBundleIdentifier</key>
                <string>com.apple.LLDB.framework</string>
                <key>CFBundleName</key>
                <string>LLDB</string>
                <key>CFBundleShortVersionString</key>
                <string>1.159</string>
                <key>CFBundleVersion</key>
                <string>159</string>
                <key>path</key>
                <string>/System/Library/PrivateFrameworks/LLDB.framework/Versions/A/Resources/Info.plist</string>
                <key>type</key>
                <string>bundle</string>
            </dict>
            <dict>
                <key>CFBundleIdentifier</key>
                <string>com.apple.lldb.launcherRootXPCService</string>
                <key>CFBundleName</key>
                <string>com.apple.lldb.launcherRootXPCService</string>
                <key>CFBundleShortVersionString</key>
                <string>1.0</string>
                <key>CFBundleVersion</key>
                <string>159</string>
                <key>path</key>
                <string>/System/Library/PrivateFrameworks/LLDB.framework/XPCServices/com.apple.lldb.launcherRootXPCService.xpc</string>
                <key>type</key>
                <string>bundle</string>
            </dict>
            <dict>
                <key>CFBundleIdentifier</key>
                <string>com.apple.lldb.launcherXPCService</string>
                <key>CFBundleName</key>
                <string>com.apple.lldb.launcherXPCService</string>
                <key>CFBundleShortVersionString</key>
                <string>1.0</string>
                <key>CFBundleVersion</key>
                <string>159</string>
                <key>path</key>
                <string>/System/Library/PrivateFrameworks/LLDB.framework/XPCServices/com.apple.lldb.launcherXPCService.xpc</string>
                <key>type</key>
                <string>bundle</string>
            </dict>
            <dict>
                <key>CFBundleIdentifier</key>
                <string>com.apple.dt.sdk.OSX10_8</string>
                <key>CFBundleName</key>
                <string>OSX 10.8 SDK</string>
                <key>CFBundleShortVersionString</key>
                <string>1.0</string>
                <key>path</key>
                <string>/usr/share/current-os.sdk/Info.plist</string>
                <key>type</key>
                <string>bundle</string>
            </dict>
        </array>
    </dict>
    </plist>
