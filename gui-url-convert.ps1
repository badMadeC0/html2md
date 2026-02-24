<#
WPF GUI for html2md
- Auto‑detects STA/MTA
- Relaunches in STA if necessary
- No WinForms (avoids freezes caused by OneDrive/VSCode/ISE)
- Safe for double-click or PowerShell execution
#>

param([string]$BatchFile, [string]$BatchOutDir, [switch]$BatchWholePage)

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
            # Default to main content unless BatchWholePage is set
            $argsList = @("--url", "$url", "--outdir", "$outDir", "--all-formats")
            if (-not $BatchWholePage) { $argsList += "--main-content" }

            if (Test-Path -LiteralPath $venvExe) {
                & $venvExe $argsList
            } elseif (Test-Path -LiteralPath $pyScript) {
                $pyCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
                $argsList = @("$pyScript") + $argsList
                & $pyCmd $argsList
            } else {
                Write-Error "Could not find html2md executable or script."
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

        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10" AcceptsReturn="True" VerticalScrollBarVisibility="Auto" Height="80"
                 ToolTip="Enter URLs to convert, one per line (Ctrl+Enter to convert)"/>

        <StackPanel Grid.Row="2" Orientation="Horizontal">
            <TextBox Name="OutBox" Width="340" FontSize="14" AutomationProperties.Name="Output Directory" ToolTip="Directory where files will be saved"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">_Browse...</Button>
            <Button Name="OpenFolderBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">_Open Folder</Button>
        </StackPanel>

        <CheckBox Name="WholePageChk" Grid.Row="3" Content="Convert _Whole Page"
                  VerticalAlignment="Center" HorizontalAlignment="Left" Margin="0,15,0,0"
                  ToolTip="If checked, includes headers and footers. Default is main content only."/>

        <Button Name="ConvertBtn" Grid.Row="3" Content="_Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion process (Ctrl+Enter)"
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
$StatusText = $window.FindName("StatusText")
$ProgressBar = $window.FindName("ProgressBar")
$LogBox = $window.FindName("LogBox")

# --- Keyboard Shortcuts ---
$UrlBox.Add_KeyDown({
    param($sender, $e)
    # Check for Ctrl + Enter
    if ($e.Key -eq [System.Windows.Input.Key]::Return -and
       ([System.Windows.Input.Keyboard]::Modifiers -band [System.Windows.Input.ModifierKeys]::Control)) {

        # Programmatically click the Convert button
        $peer = New-Object System.Windows.Automation.Peers.ButtonAutomationPeer($ConvertBtn)
        $invoker = $peer.GetPattern([System.Windows.Automation.Peers.PatternInterface]::Invoke)
        $invoker.Invoke()

        $e.Handled = $true
    }
})

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
            $uriObj = [System.Uri]$url
            if ($uriObj.Scheme -notmatch '^https?$') {
                throw "Invalid scheme for URL: $url"
            }
        } catch {
            [System.Windows.MessageBox]::Show("Please enter a valid HTTP/HTTPS URL. One or more URLs are invalid.","Invalid URL","OK","Error") | Out-Null
            $ProgressBar.IsIndeterminate = $false
            return
        }
    }
    # ---------------------------

    # Reject quotes and other dangerous metacharacters in outdir for defense-in-depth
    if ($outdir -match '[&|;<>^"]' -or $outdir -match '%') {
        [System.Windows.MessageBox]::Show("Invalid characters detected in output directory.","Security Warning","OK","Warning") | Out-Null
        return
    }
    
    if (-not (Test-Path $outdir)) {
        try { New-Item -ItemType Directory -Path $outdir -Force | Out-Null }
        catch {}
    }

    $scriptDir = Split-Path -Parent $PSCommandPath
    if (-not $scriptDir) {
        $scriptDir = (Get-Location).Path
    }

    $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
    $pyScript = Join-Path $scriptDir "src\html2md\cli.py"

    # Attempt to use Short Path (8.3) to bypass cmd.exe issues with '&'
    try {
        $fso = New-Object -ComObject Scripting.FileSystemObject
        $short = $fso.GetFolder($scriptDir).ShortPath
        if ($short) { $scriptDir = $short }
    } catch {}

    # Check for Python executable
    $pyCmd = "python"
    if (-not (Get-Command $pyCmd -ErrorAction SilentlyContinue)) {
        if (Get-Command "python3" -ErrorAction SilentlyContinue) { $pyCmd = "python3" }
        else {
            $StatusText.Text = "Error: Python not found in PATH."
            $StatusText.Foreground = "Red"
            $LogBox.AppendText("ERROR: 'python' command not found. Please install Python.`r`n")
            $ProgressBar.IsIndeterminate = $false
            return
        }
    }

    # Use a robust way to launch the process:
    # 1. Revert to ProcessStartInfo for precise control over the command line.
    # 2. Use the "double-quote wrapper" for cmd /c (i.e., /c ""command" args")
    #    to ensure all internal quotes are preserved and arguments are correctly delimited.
    # 3. Explicitly quote each argument to prevent metacharacters like & from being interpreted.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.WorkingDirectory = $scriptDir
    $psi.UseShellExecute = $true

    if ($urlList.Count -gt 1) {
        # --- BATCH MODE ---
        $LogBox.AppendText("Batch mode detected ($($urlList.Count) URLs).`r`n")
        $tempFile = [System.IO.Path]::GetTempFileName()
        $urlList | Set-Content -Path $tempFile

        # Sanitize for -File arguments (escape single quotes)
        $safeCommandPath = $PSCommandPath -replace "'", "''"
        $safeTempFile = $tempFile -replace "'", "''"
        $safeOutDir = $outdir -replace "'", "''"

        # Relaunch this script in batch mode
        # Use single quotes for arguments to avoid variable expansion and allow containing spaces/special chars
        $psi.Arguments = "-NoExit -ExecutionPolicy Bypass -File '$safeCommandPath' -BatchFile '$safeTempFile' -BatchOutDir '$safeOutDir'"
        if ($WholePageChk.IsChecked) {
            $psi.Arguments += " -BatchWholePage"
        }
    } else {
        # --- SINGLE URL MODE ---
        $url = $urlList[0]
        # If Whole Page is unchecked, we add the flag to ignore headers/footers
        $optArg = if (-not $WholePageChk.IsChecked) { " --main-content" } else { "" }

        # Sanitize inputs for single-quoted string interpolation in PowerShell
        $safeUrl = $url -replace "'", "''"
        $safeOutDir = $outdir -replace "'", "''"
        $safeVenvExe = $venvExe -replace "'", "''"
        $safePyScript = $pyScript -replace "'", "''"

        if (Test-Path -LiteralPath $venvExe) {
            $LogBox.AppendText("Found venv executable: $venvExe`r`n")
            $psi.Arguments = "-NoExit -Command `"& '$safeVenvExe' --url '$safeUrl' --outdir '$safeOutDir' --all-formats$optArg`""
        }
        elseif (Test-Path -LiteralPath $pyScript) {
            $LogBox.AppendText("Found Python script: $pyScript`r`n")
            $psi.Arguments = "-NoExit -Command `"& $pyCmd '$safePyScript' --url '$safeUrl' --outdir '$safeOutDir' --all-formats$optArg`""
        }
        else {
            $StatusText.Text = "Error: html2md executable not found."
            $StatusText.Foreground = "Red"
            $LogBox.AppendText("ERROR: Could not find .venv\Scripts\html2md.exe or html2md.py in $scriptDir`r`n")
            $LogBox.AppendText("Have you run setup-html2md.ps1?`r`n")
            $ProgressBar.IsIndeterminate = $false
            return
        }
    }
    
    $LogBox.AppendText("Executing process...`r`n")
    [Diagnostics.Process]::Start($psi) | Out-Null

    $StatusText.Text = "Conversion started in a new console."
    $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
    $ProgressBar.IsIndeterminate = $false
})

# --- Show window ---
$window.ShowDialog() | Out-Null
