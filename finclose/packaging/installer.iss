; FinClose 설치 파일(Inno Setup 6). 관리자 권한 없이 현재 사용자에게 설치한다.
; 빌드: iscc /DAppVersion=0.1.0 packaging\installer.iss  (먼저 build_desktop.py 실행)
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{6F7E2C1A-3B9D-4E55-9A41-FC10CE0A1D01}
AppName=FinClose AI
AppVersion={#AppVersion}
AppPublisher=FinClose (사내 시험 버전)
DefaultDirName={localappdata}\Programs\FinClose
DefaultGroupName=FinClose
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=FinClose-Setup-{#AppVersion}
SetupIconFile=..\build\finclose.ico
UninstallDisplayIcon={app}\FinClose.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 아이콘 만들기"; GroupDescription: "추가 작업:"

[Files]
Source: "..\dist\FinClose\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\FinClose"; Filename: "{app}\FinClose.exe"
Name: "{group}\FinClose 연습모드"; Filename: "{app}\FinClose.exe"; Parameters: "--demo"
Name: "{group}\FinClose 사용설명서"; Filename: "{app}\사용설명서.html"
Name: "{group}\FinClose 제거"; Filename: "{uninstallexe}"
Name: "{autodesktop}\FinClose"; Filename: "{app}\FinClose.exe"; Tasks: desktopicon
Name: "{autodesktop}\FinClose 연습모드"; Filename: "{app}\FinClose.exe"; Parameters: "--demo"; Tasks: desktopicon

[Run]
Filename: "{app}\FinClose.exe"; Parameters: "--demo"; Description: "연습 모드로 바로 실행해 보기"; Flags: nowait postinstall skipifsilent

; 제거해도 문서\FinClose(업무 데이터)는 지우지 않는다.
