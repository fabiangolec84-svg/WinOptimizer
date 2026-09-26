; Script generated for WinOptimizer 2.0 Pro
; Inno Setup 6 Script with Modern Windows 11 Dark Aesthetic

#define MyAppName "WinOptimizer"
#define MyAppVersion "2.0 Pro"
#define MyAppPublisher "WinOptimizer"
#define MyAppURL "https://github.com/winoptimizer"
#define MyAppExeName "WinOptimizer.exe"

[Setup]
AppId={{8B452793-4E8C-4C96-BD42-6F1E3A426910}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\WinOptimizer
DefaultGroupName=WinOptimizer
AllowNoIcons=yes
LicenseFile=installer_license.txt
OutputDir=dist_installer
OutputBaseFilename=WinOptimizer_Setup_v2.0_Pro
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName=WinOptimizer 2.0 Pro
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern dark windows11 hidebevels
WizardImageFile=assets\wizard_large.bmp
WizardSmallImageFile=assets\wizard_small.bmp
WizardBackColor=#0b0f19
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UsedUserAreasWarning=no
CloseApplications=force
RestartApplications=no

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[CustomMessages]
polish.LaunchProgram=Uruchom program WinOptimizer 2.0 Pro teraz
polish.CreateDesktopIcon=Utwórz skrót na Pulpicie
polish.AdditionalIcons=Dodatkowe ikony:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\WinOptimizer"
