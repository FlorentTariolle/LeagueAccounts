[Setup]
AppName=League Accounts
AppVersion=1.1
DefaultDirName={autopf}\LeagueAccounts
DefaultGroupName=League Accounts
OutputDir=../dist
OutputBaseFilename=LeagueAccountsSetup
SetupIconFile=icon.ico

[Files]
Source: "..\\dist\\leagueaccounts.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\\League Accounts"; Filename: "{app}\\leagueaccounts.exe"
Name: "{commondesktop}\\League Accounts"; Filename: "{app}\\leagueaccounts.exe"