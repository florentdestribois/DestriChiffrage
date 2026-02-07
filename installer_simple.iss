; Script Inno Setup pour DestriChiffrage - Version Simplifiée
; Génère un installateur Windows professionnel

[Setup]
; Informations de base
AppId={{C8F42A3E-5E4D-4B2C-9A8E-1D2F3C4B5A6E}
AppName=DestriChiffrage
AppVersion=1.3.4
AppPublisher=Destribois
AppPublisherURL=https://github.com/florentdestribois/DestriChiffrage
AppSupportURL=https://github.com/florentdestribois/DestriChiffrage
AppUpdatesURL=https://github.com/florentdestribois/DestriChiffrage
DefaultDirName={autopf}\DestriChiffrage
DefaultGroupName=DestriChiffrage
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=DestriChiffrage-Setup-1.3.4
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

; Privilèges
PrivilegesRequired=admin

; Dossier de désinstallation
UninstallDisplayIcon={app}\DestriChiffrage.exe

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Exécutable principal
Source: "dist\DestriChiffrage.exe"; DestDir: "{app}"; Flags: ignoreversion

; Fichiers de support (si présents dans dist\)
; IMPORTANT: On exclut data ET config pour préserver les données utilisateur lors des mises à jour
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data,config"

[Dirs]
; Créer les dossiers data
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\data\Fiches_techniques"; Permissions: users-modify
Name: "{app}\data\Devis_fournisseur"; Permissions: users-modify
Name: "{app}\config"; Permissions: users-modify

[Icons]
; Raccourci dans le menu Démarrer
Name: "{group}\DestriChiffrage"; Filename: "{app}\DestriChiffrage.exe"
Name: "{group}\{cm:UninstallProgram,DestriChiffrage}"; Filename: "{uninstallexe}"

; Raccourci sur le bureau (optionnel)
Name: "{autodesktop}\DestriChiffrage"; Filename: "{app}\DestriChiffrage.exe"; Tasks: desktopicon

; Raccourci barre de lancement rapide (Windows 7 et antérieur)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\DestriChiffrage"; Filename: "{app}\DestriChiffrage.exe"; Tasks: quicklaunchicon

[Run]
; Proposer de lancer l'application après installation
Filename: "{app}\DestriChiffrage.exe"; Description: "{cm:LaunchProgram,DestriChiffrage}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Nettoyer les fichiers temporaires
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{app}\*.pyc"
