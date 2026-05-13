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

    # Check if this is a temp file created by the GUI (temp files are in %TEMP%)
    $isTempFile = $BatchFile -like "$env:TEMP\*"

    $scriptDir = Split-Path -Parent $PSCommandPath
    if (-not $scriptDir) { $scriptDir = (Get-Location).Path }

    $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
    $pyScript = Join-Path $scriptDir "html2md.py"
    $outDir = if (-not [string]::IsNullOrWhiteSpace($BatchOutDir)) { $BatchOutDir } else { "$env:USERPROFILE\Downloads" }

    try {
        $urls = Get-Content -LiteralPath $BatchFile
        foreach ($line in $urls) {
            $url = $line.Trim()
            if ([string]::IsNullOrWhiteSpace($url)) { continue }

            # Security Validation
            $uriOut = $null
            if ([System.Uri]::TryCreate($url, [System.UriKind]::Absolute, [ref]$uriOut) -and $uriOut.Scheme -match '^https?$') {
                $url = $uriOut.AbsoluteUri
            } else {
                Write-Error "Invalid URL skipped: $url"
                continue
            }

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
    } finally {
        # Clean up temp file if it was created by the GUI
        if ($isTempFile -and (Test-Path -LiteralPath $BatchFile)) {
            try {
                Remove-Item -LiteralPath $BatchFile -Force -ErrorAction SilentlyContinue
                Write-Host "Cleaned up temporary batch file: $BatchFile"
            } catch {
                Write-Warning "Could not delete temporary file: $BatchFile"
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

if ($null -ne $IsWindows -and -not $IsWindows) {
    Write-Error "This GUI script requires Windows Presentation Foundation (WPF) and is not supported on macOS or Linux."
    exit 1
}

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
                <Button Name="ClearBtn" Content="Clea_r" Height="22" Width="60" ToolTip="URL list is already empty" IsEnabled="False"/>
            </StackPanel>
        </Grid>

        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10" AcceptsReturn="True"
                 VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Auto" Height="80"
                 ToolTip="Enter one or more URLs (one per line)"/>

        <Grid Grid.Row="2" VerticalAlignment="Center">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Label Name="OutBoxLabel" Grid.Column="0" Content="_Save To:" Target="{Binding ElementName=OutBox}" FontSize="14" VerticalAlignment="Center" Margin="0,0,5,0"/>
            <TextBox Grid.Column="1" Name="OutBox" FontSize="14" AutomationProperties.LabeledBy="{Binding ElementName=OutBoxLabel}" ToolTip="Directory where files will be saved" VerticalContentAlignment="Center"/>
            <Button Grid.Column="2" Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">_Browse...</Button>
            <Button Grid.Column="3" Name="OpenFolderBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">_Open Folder</Button>
        </Grid>

        <CheckBox Name="WholePageChk" Grid.Row="3" Content="Convert _Whole Page"
                  VerticalAlignment="Center" HorizontalAlignment="Left" Margin="0,15,0,0"
                  ToolTip="If checked, includes headers and footers. Default is main content only."/>

        <Button Name="ConvertBtn" Grid.Row="3" Content="_Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                IsEnabled="False"
                ToolTip="Please enter at least one URL to enable conversion"
                />

        <ProgressBar Name="ProgressBar" Grid.Row="4" Height="10" Margin="0,10,0,0" IsIndeterminate="False" AutomationProperties.Name="Conversion Progress"/>
        
        <TextBox Name="LogBox" Grid.Row="5" Margin="0,10,0,0" FontFamily="Consolas" FontSize="12"
                 TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" IsReadOnly="True" AutomationProperties.Name="Log Output"
                 Text="Ready. Conversion logs will appear here..."/>

        <StatusBar Grid.Row="6" Margin="0,10,0,0">
            <TextBlock Name="StatusText" Text="Ready" Foreground="#555555"/>
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

# --- Dynamic Convert button state ---
$UrlBox.Add_TextChanged({
    if ([string]::IsNullOrWhiteSpace($UrlBox.Text)) {
        $ConvertBtn.IsEnabled = $false
        $ConvertBtn.ToolTip = "Please enter at least one URL to enable conversion"
        $ClearBtn.IsEnabled = $false
        $ClearBtn.ToolTip = "URL list is already empty"
    } else {
        $ConvertBtn.IsEnabled = $true
        $ConvertBtn.ToolTip = "Start conversion process"
        $ClearBtn.IsEnabled = $true
        $ClearBtn.ToolTip = "Clear URL list"
    }
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

    # --- Security Validation & Sanitization ---
    $validatedUrls = New-Object System.Collections.Generic.List[string]
    foreach ($u in $urlList) {
        $uriOut = $null
        if ([System.Uri]::TryCreate($u, [System.UriKind]::Absolute, [ref]$uriOut) -and $uriOut.Scheme -match '^https?$') {
            # AbsoluteUri is properly percent-encoded, preventing quote-based injection
            $validatedUrls.Add($uriOut.AbsoluteUri)
        } else {
            [System.Windows.MessageBox]::Show("Invalid URL detected: $u`n`nPlease enter valid HTTP/HTTPS URLs.","Invalid URL","OK","Error") | Out-Null
            $ProgressBar.IsIndeterminate = $false
            return
        }
    }
    $urlList = $validatedUrls.ToArray()

    # Reject quotes and other dangerous metacharacters in outdir for defense-in-depth.
    # We allow (), [], and % as they are common/safe in Windows paths when properly quoted.
    if ($outdir -match '[&|;<>^"]') {
        [System.Windows.MessageBox]::Show("Invalid characters detected in output directory (e.g. quotes or redirects).","Security Warning","OK","Warning") | Out-Null
        $ProgressBar.IsIndeterminate = $false
        return
    }
    # ---------------------------

    if (-not (Test-Path -LiteralPath $outdir)) {
        try { New-Item -ItemType Directory -LiteralPath $outdir -Force | Out-Null }
        catch {}
    }

    $scriptDir = Split-Path -Parent $PSCommandPath
    if (-not $scriptDir) {
        $scriptDir = (Get-Location).Path
    }

    # Attempt to use Short Path (8.3) to avoid path-escaping issues in PowerShell/CMD
    try {
        $fso = New-Object -ComObject Scripting.FileSystemObject
        $short = $fso.GetFolder($scriptDir).ShortPath
        if ($short) { $scriptDir = $short }
    } catch {}

    # Initialize paths to html2md executable and script
    $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
    $pyScript = Join-Path $scriptDir "html2md.py"

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
    # 2. Use powershell.exe with -NoProfile to avoid side effects and keep the window open with -NoExit.
    # 3. Use -File for batch mode and -Command with proper quoting for single URL mode.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $powershellPath = Join-Path $PSHOME "powershell.exe"
    if (-not (Test-Path -LiteralPath $powershellPath)) { $powershellPath = "powershell.exe" }
    $psi.FileName = $powershellPath
    $psi.WorkingDirectory = $scriptDir
    $psi.UseShellExecute = $true

    if ($urlList.Count -gt 1) {
        # --- BATCH MODE ---
        $LogBox.AppendText("Batch mode detected ($($urlList.Count) URLs).`r`n")
        $tempFile = [System.IO.Path]::GetTempFileName()
        $urlList | Set-Content -LiteralPath $tempFile

        # Normalize outdir to avoid trailing backslash issues with Windows command-line parsing
        # A trailing backslash can escape the closing quote in "C:\"
        $normalizedOutDir = $outdir.TrimEnd('\')
        if ($normalizedOutDir.Length -eq 2 -and $normalizedOutDir.EndsWith(':')) {
            # Drive root like "C:" needs the backslash
            $normalizedOutDir += '\'
        }

        # Sanitize for -File arguments by using double quotes to handle spaces
        # Windows command line splitting treats " as the primary quote character.
        $safeCommandPath = "`"$PSCommandPath`""
        $safeTempFile = "`"$tempFile`""
        $safeOutDir = "`"$normalizedOutDir`""

        # Relaunch this script in batch mode
        # Use -File with double-quoted paths for robust Windows command-line handling
        # Pass the temp file path so the batch process can clean it up
        $psi.Arguments = "-NoExit -NoProfile -ExecutionPolicy Bypass -File $safeCommandPath -BatchFile $safeTempFile -BatchOutDir $safeOutDir"
        if ($WholePageChk.IsChecked) {
            $psi.Arguments += " -BatchWholePage"
        }
    } else {
        # --- SINGLE URL MODE ---
        $url = $urlList[0]
        # If Whole Page is unchecked, we add the flag to ignore headers/footers
        $optArg = if (-not $WholePageChk.IsChecked) { " --main-content" } else { "" }

        # Sanitize inputs for PowerShell -Command interpolation.
        # We use double quotes around arguments and escape internal double quotes, dollar signs,
        # and backticks with the PowerShell escape character (backtick) to prevent subexpression execution.
        $safeUrl = $url -replace '["$`]', '`$0'
        $safeOutDir = $outdir -replace '["$`]', '`$0'
        $safeVenvExe = $venvExe -replace '["$`]', '`$0'
        $safePyScript = $pyScript -replace '["$`]', '`$0'

        if (Test-Path -LiteralPath $venvExe) {
            $LogBox.AppendText("Found venv executable: $venvExe`r`n")
            $psi.Arguments = "-NoExit -NoProfile -Command `"& `"$safeVenvExe`" --url `"$safeUrl`" --outdir `"$safeOutDir`" --all-formats$optArg`""
        }
        elseif (Test-Path -LiteralPath $pyScript) {
            $LogBox.AppendText("Found Python script: $pyScript`r`n")
            $psi.Arguments = "-NoExit -NoProfile -Command `"& $pyCmd `"$safePyScript`" --url `"$safeUrl`" --outdir `"$safeOutDir`" --all-formats$optArg`""
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
