; SpaceUnpack installer (Inno Setup 6). Build: ISCC.exe SpaceUnpack.iss  (needs dist\SpaceUnpack.exe first)
[Setup]
AppId={{B6E2F0C4-7A1D-4C55-9C0B-5A3E2D7F9A11}
AppName=SpaceUnpack
AppVersion=1.0
AppPublisher=SpaceUnpack
DefaultDirName={autopf}\SpaceUnpack
DefaultGroupName=SpaceUnpack
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=SpaceUnpack-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=SpaceUnpack.ico
ChangesAssociations=yes
UninstallDisplayIcon={app}\SpaceUnpack.exe
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "contextmenu"; Description: "Add SpaceUnpack to the right-click menu of archive files"
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "dist\SpaceUnpack.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SpaceUnpack"; Filename: "{app}\SpaceUnpack.exe"
Name: "{autodesktop}\SpaceUnpack"; Filename: "{app}\SpaceUnpack.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\02aShrink"; ValueType: string; ValueName: ""; ValueData: "Extract and shrink the zip as it goes (saves space)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\02aShrink\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --shrink ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.zip\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tar\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.gz\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tgz\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.bz2\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.tbz2\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.xz\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\03Low"; ValueType: string; ValueName: ""; ValueData: "Extract and free space as it goes (low-space mode)"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\03Low\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --low-space ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.txz\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.7z\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack"; ValueType: string; ValueName: "MUIVerb"; ValueData: "SpaceUnpack"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\SpaceUnpack.exe"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\01Folder"; ValueType: string; ValueName: ""; ValueData: "Extract to folder and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\01Folder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\02Here"; ValueType: string; ValueName: ""; ValueData: "Extract here and delete archive"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\02Here\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" --auto --here ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\04Open"; ValueType: string; ValueName: ""; ValueData: "Open with SpaceUnpack..."; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.rar\shell\SpaceUnpack\shell\04Open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SpaceUnpack.exe"" ""%1"""; Tasks: contextmenu
