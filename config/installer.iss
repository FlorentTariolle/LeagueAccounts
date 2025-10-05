[Setup]
AppName=League Accounts
AppVersion=1.1
DefaultDirName={autopf}\LeagueAccounts
DefaultGroupName=League Accounts
OutputDir=../../build/dist
OutputBaseFilename=LeagueAccountsSetup
SetupIconFile=../assets/icons/icon.ico
Compression=lzma2/max
SolidCompression=yes

[Files]
Source: "..\\..\\build\\dist\\leagueaccounts.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\\League Accounts"; Filename: "{app}\\leagueaccounts.exe"
Name: "{commondesktop}\\League Accounts"; Filename: "{app}\\leagueaccounts.exe"