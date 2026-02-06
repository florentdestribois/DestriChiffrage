; Script Inno Setup pour DestriChiffrage
; Génère un installateur Windows professionnel

#define MyAppName "DestriChiffrage"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Destribois"
#define MyAppURL "https://github.com/florentdestribois/DestriChiffrage"
#define MyAppExeName "DestriChiffrage.exe"

[Setup]
; Informations de base
AppId={{C8F42A3E-5E4D-4B2C-9A8E-1D2F3C4B5A6E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=DestriChiffrage-Setup-{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

; Privilèges
PrivilegesRequired=lowest

; Dossier de désinstallation
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Exécutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Fichiers de support (si présents dans dist\)
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data"

; Dossier data - Créé vide, sera rempli par l'application
; (On ne copie pas le contenu pour préserver les données utilisateur)

[Dirs]
; Créer les dossiers data
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\data\Fiches_techniques"; Permissions: users-modify
Name: "{app}\data\Devis_fournisseur"; Permissions: users-modify
Name: "{app}\config"; Permissions: users-modify

[Icons]
; Raccourci dans le menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Raccourci sur le bureau (optionnel)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Raccourci barre de lancement rapide (Windows 7 et antérieur)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Proposer de lancer l'application après installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Nettoyer les fichiers temporaires
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{app}\*.pyc"

[Code]
// Vérifier si une ancienne version est installée
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  UninstallString: String;
begin
  Result := True;

  // Vérifier si une version précédente est installée
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{C8F42A3E-5E4D-4B2C-9A8E-1D2F3C4B5A6E}_is1',
    'UninstallString', UninstallString) then
  begin
    // Une version est déjà installée
    if MsgBox('Une version de DestriChiffrage est déjà installée. Voulez-vous la désinstaller ?',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Désinstaller l'ancienne version
      Exec(UninstallString, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
      Result := True;
    end
    else
      Result := False; // Annuler l'installation
  end;
end;

// Message de bienvenue personnalisé
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'Cet assistant va installer DestriChiffrage sur votre ordinateur.' + #13#10 +
    #13#10 +
    'DestriChiffrage est une application de gestion de catalogue et de chiffrage.' + #13#10 +
    #13#10 +
    'Cliquez sur Suivant pour continuer.';
end;
