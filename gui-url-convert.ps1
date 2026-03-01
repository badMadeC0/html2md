<#
WPF GUI for html2md
- Auto‑detects STA/MTA
- Relaunches in STA if necessary
- No WinForms (avoids freezes caused by OneDrive/VSCode/ISE)
- Safe for double-click or PowerShell execution
#>

param([string]$BatchFile, [string]$BatchOutDir, [switch]$BatchWholePage, [switch]$BatchAllFormats)

function Get-UniquePath {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $Path }
    
    $dir = Split-Path -Parent $Path
    $name = [System.IO.Path]::GetFileNameWithoutExtension($Path)
    $ext = [System.IO.Path]::GetExtension($Path)
    $count = 1
    
    do {
        $newPath = Join-Path $dir "${name}_${count}${ext}"
        $count++
    } while (Test-Path -LiteralPath $newPath)
    
    return $newPath
}

if ($BatchFile) {
    if (-not (Test-Path -LiteralPath $BatchFile)) {
        Write-Error "Batch file not found: $BatchFile"
        exit 1
    }
    $scriptDir = Split-Path -Parent $PSCommandPath
    if (-not $scriptDir) { $scriptDir = (Get-Location).Path }

    $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
    $pyScript = Join-Path $scriptDir "html2md.py"
    $outDir = if (-not [string]::IsNullOrWhiteSpace($BatchOutDir)) { $BatchOutDir } else { "$env:USERPROFILE\Downloads" }

    Get-Content -LiteralPath $BatchFile | ForEach-Object {
        $url = $_.Trim()
        if (-not [string]::IsNullOrWhiteSpace($url)) {
            Write-Host "Processing: $url"
            $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

            # Default to main content unless BatchWholePage is set
            $argsList = @("--url", "$url", "--outdir", "$tempDir")
            if ($BatchAllFormats) {
                $argsList += "--all-formats"
            }

            try {
                if (Test-Path -LiteralPath $venvExe) {
                    & $venvExe $argsList
                } elseif (Test-Path -LiteralPath $pyScript) {
                    $pyCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
                    $argsList = @("$pyScript") + $argsList
                    & $pyCmd $argsList
                } else {
                    Write-Error "Could not find html2md executable or script."
                }

                Get-ChildItem -Path $tempDir | ForEach-Object {
                    $dest = Join-Path $outDir $_.Name
                    $final = Get-UniquePath $dest
                    Move-Item -LiteralPath $_.FullName -Destination $final -Force
                    Write-Host "Saved to: $final"
                }
            } finally {
                if (Test-Path -LiteralPath $tempDir) { Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue }
            }
        }
    }
    exit
}

# --- Relaunch in STA mode if needed ---
# if ([Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
#     Write-Host "[INFO] Relaunching in STA mode..."
#     $psi = New-Object System.Diagnostics.ProcessStartInfo
#     $psi.FileName = "powershell.exe"
#     $psi.Arguments = "-STA -ExecutionPolicy Bypass -File `"$PSCommandPath`""
#     $psi.UseShellExecute = $true
#     [Diagnostics.Process]::Start($psi) | Out-Null
#     exit
# }

# --- Load WPF assemblies ---
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml
Add-Type -AssemblyName System.Windows.Forms

# --- Define XAML UI ---
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        Title="html2md - Convert URL"
        Height="450" Width="580"
        FocusManager.FocusedElement="{Binding ElementName=UrlBox}"
        WindowStartupLocation="CenterScreen"
        Topmost="True">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <Grid>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Label Content="_Paste URL(s):" Target="{Binding ElementName=UrlBox}" FontSize="14" VerticalAlignment="Bottom"/>
            <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Bottom" Margin="0,0,0,2">
                <Button Name="PasteBtn" Content="Pas_te" Height="22" Width="60" Margin="0,0,5,0" ToolTip="Paste from Clipboard"/>
                <Button Name="ClearBtn" Content="Clea_r" Height="22" Width="60" ToolTip="Clear URL list"/>
            </StackPanel>
        </Grid>

        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10" AcceptsReturn="True" VerticalScrollBarVisibility="Auto" Height="80"/>

        <Grid Grid.Row="2">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Label Content="_Output:" Target="{Binding ElementName=OutBox}" FontSize="14" VerticalAlignment="Center" Margin="0,0,5,0"/>
            <TextBox Name="OutBox" Grid.Column="1" FontSize="14" VerticalContentAlignment="Center" AutomationProperties.Name="Output Directory" ToolTip="Directory where files will be saved"/>
            <Button Name="BrowseBtn" Grid.Column="2" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">_Browse...</Button>
            <Button Name="OpenFolderBtn" Grid.Column="3" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">_Open Folder</Button>
        </Grid>

        <CheckBox Name="WholePageChk" Grid.Row="3" Content="Convert _Whole Page"
                  VerticalAlignment="Center" HorizontalAlignment="Left" Margin="0,15,0,0"
                  ToolTip="If checked, includes headers and footers. Default is main content only."/>

        <CheckBox Name="AllFormatsChk" Grid.Row="3" Content="Generate _All Formats (md, txt, pdf)" IsChecked="False"
                  VerticalAlignment="Center" HorizontalAlignment="Left" Margin="150,15,0,0"
                  ToolTip="If checked, creates .md, .txt, and .pdf files. Uncheck if the converter doesn't support this."/>

        <Button Name="ConvertBtn" Grid.Row="3" Content="_Convert"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion process"
                />

        <ProgressBar Name="ProgressBar" Grid.Row="4" Height="10" Margin="0,10,0,0" IsIndeterminate="False" AutomationProperties.Name="Conversion Progress"/>
        
        <TextBox Name="LogBox" Grid.Row="5" Margin="0,10,0,0" FontFamily="Consolas" FontSize="12"
                 TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" IsReadOnly="True" AutomationProperties.Name="Log Output"/>

        <StatusBar Grid.Row="6" Margin="0,10,0,0">
            <TextBlock Name="StatusText" Text="Ready" Foreground="Gray"/>
        </StatusBar>
    </Grid>
</Window>
"@

# --- Parse XAML ---
$xmlDoc = [xml]$xaml
$reader = New-Object System.Xml.XmlNodeReader $xmlDoc
$window = [Windows.Markup.XamlReader]::Load($reader)

# Fallback if encoding issues persist:
# $bytes = [System.Text.Encoding]::UTF8.GetBytes($xaml)
# $window = [Windows.Markup.XamlReader]::Load((New-Object System.IO.MemoryStream (,$bytes)))

# --- Get controls ---
$UrlBox = $window.FindName("UrlBox")
$OutBox = $window.FindName("OutBox")
$BrowseBtn = $window.FindName("BrowseBtn")
$OpenFolderBtn = $window.FindName("OpenFolderBtn")
$ConvertBtn = $window.FindName("ConvertBtn")
$PasteBtn = $window.FindName("PasteBtn")
$ClearBtn = $window.FindName("ClearBtn")
$WholePageChk = $window.FindName("WholePageChk")
$AllFormatsChk = $window.FindName("AllFormatsChk")
$StatusText = $window.FindName("StatusText")
$ProgressBar = $window.FindName("ProgressBar")
$LogBox = $window.FindName("LogBox")

# Set default output to Downloads
$OutBox.Text = "$env:USERPROFILE\Downloads"

# --- Browse button logic ---
$BrowseBtn.Add_Click({
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($dlg.ShowDialog() -eq "OK") {
        $OutBox.Text = $dlg.SelectedPath
    }
})

# --- Open Folder button logic ---
$OpenFolderBtn.Add_Click({
    $path = $OutBox.Text.Trim()
    if (Test-Path -LiteralPath $path) {
        Invoke-Item -LiteralPath $path
    } else {
        $StatusText.Text = "Output folder does not exist."
        $StatusText.Foreground = "Red"
    }
})

function Get-ClipboardTextSta {
    <#
    Executes clipboard text access on a temporary STA thread so the GUI
    works even when the main runspace is MTA (e.g., in PowerShell 7).
    Returns an object with:
      - HasText : [bool]  - true if clipboard contains text
      - Text    : [string] - the clipboard text (may be $null)
    #>
    $state = New-Object psobject -Property @{
        HasText = $false
        Text    = $null
    }

    try {
        $thread = New-Object System.Threading.Thread({
            param($s)
            if ([System.Windows.Clipboard]::ContainsText()) {
                $s.HasText = $true
                $s.Text = [System.Windows.Clipboard]::GetText()
            } else {
                $s.HasText = $false
                $s.Text = $null
            }
        })

        $thread.SetApartmentState([System.Threading.ApartmentState]::STA)
        $thread.Start($state)
        $thread.Join()
    } catch {
        # Swallow here; caller will handle generic error messaging.
    }

    return $state
}

# --- Paste button logic ---
$PasteBtn.Add_Click({
    try {
        $clipboardState = Get-ClipboardTextSta

        if ($clipboardState -and $clipboardState.HasText) {
            $text = $clipboardState.Text
            if (-not [string]::IsNullOrWhiteSpace($text)) {
                if ($UrlBox.Text.Length -gt 0 -and -not $UrlBox.Text.EndsWith("`n")) {
                    $UrlBox.AppendText("`r`n")
                }
                $UrlBox.AppendText($text)
                $UrlBox.Focus()
                $UrlBox.ScrollToEnd()
                $StatusText.Text = "Pasted from clipboard."
                $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
            } else {
                $StatusText.Text = "Clipboard is empty or whitespace."
                $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
            }
        } else {
            $StatusText.Text = "Clipboard does not contain text."
            $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
        }
    } catch {
        $StatusText.Text = "Error pasting from clipboard."
        $StatusText.Foreground = "Red"
        $StatusText.Foreground = "Red"
    }
})

# --- Clear button logic ---
$ClearBtn.Add_Click({
    $UrlBox.Clear()
    $UrlBox.Focus()
    $StatusText.Text = "Cleared."
    $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
})

# --- Convert button logic ---
$ConvertBtn.Add_Click({
    $rawInput = $UrlBox.Text
    $urlList = @($rawInput -split "`r`n|`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_.Trim() })
    $outdir = $OutBox.Text.Trim()

    $LogBox.Text = "--- Starting Conversion ---`r`n"
    $ProgressBar.IsIndeterminate = $true

    if ($urlList.Count -eq 0) {
        $StatusText.Text = "Please enter a URL."
        $StatusText.Foreground = "Red"
        $ProgressBar.IsIndeterminate = $false
        return
    }

        # --- Security Validation ---
        foreach ($url in $urlList) {
            try {
                if (-not ($url -match '^https?://')) {
                    throw "URL must start with http:// or https://"
                }
            } catch {
                $StatusText.Text = "Invalid URL: $_"
                $StatusText.Foreground = "Red"
                $ProgressBar.IsIndeterminate = $false
                return
            }
        }
    
        # --- Execute Conversion ---
        $scriptDir = Split-Path -Parent $PSCommandPath
        if (-not $scriptDir) { $scriptDir = (Get-Location).Path }
    
        $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
        $pyScript = Join-Path $scriptDir "html2md.py"
    
        $successCount = 0
        $failureCount = 0
    
        foreach ($url in $urlList) {
            $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

            try {
                $StatusText.Text = "Converting: $url"
                $argsList = @("--url", $url, "--outdir", $tempDir)
    
                if ($WholePageChk.IsChecked) {
                    $argsList += "--whole-page"
                }

                if ($AllFormatsChk.IsChecked) {
                    $argsList += "--all-formats"
                }
    
                if (Test-Path -LiteralPath $venvExe) {
                    $output = & $venvExe $argsList 2>&1
                    if ($output) { $LogBox.AppendText(($output | Out-String)) }
                    if ($LASTEXITCODE -ne 0) {
                        throw "Process exited with code $LASTEXITCODE."
                    }
                } elseif (Test-Path -LiteralPath $pyScript) {
                    $pyCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
                    $output = & $pyCmd $pyScript $argsList 2>&1
                    if ($output) { $LogBox.AppendText(($output | Out-String)) }
                    if ($LASTEXITCODE -ne 0) {
                        throw "Process exited with code $LASTEXITCODE."
                    }
                } else {
                    throw "Could not find html2md executable or script."
                }

                Get-ChildItem -Path $tempDir | ForEach-Object {
                    $dest = Join-Path $outdir $_.Name
                    $final = Get-UniquePath $dest
                    Move-Item -LiteralPath $_.FullName -Destination $final -Force
                    $LogBox.AppendText("Saved to: $final`r`n")
                }
    
                $successCount++
                $LogBox.AppendText("[OK] Completed: $url`r`n")
            } catch {
                $failureCount++
                $LogBox.AppendText("[Error] Failed: $url`r`n  Error: $_`r`n")
            } finally {
                if (Test-Path -LiteralPath $tempDir) { Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue }
            }
        }
    
        $ProgressBar.IsIndeterminate = $false
        $StatusText.Text = "Complete: $successCount succeeded, $failureCount failed"
        $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
    })
    
    # --- Show window ---
    $window.ShowDialog() | Out-Null
 