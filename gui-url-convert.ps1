<#
WPF GUI for html2md
- Auto‑detects STA/MTA
- Relaunches in STA if necessary
- No WinForms (avoids freezes caused by OneDrive/VSCode/ISE)
- Safe for double-click or PowerShell execution
#>

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

        <Label Content="_Paste URL:" Target="{Binding ElementName=UrlBox}" FontSize="14"/>
        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10"/>

        <StackPanel Grid.Row="2" Orientation="Horizontal">
            <TextBox Name="OutBox" Width="340" FontSize="14" AutomationProperties.Name="Output Directory"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">Browse...</Button>
            <Button Name="OpenFolderBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">Open Folder</Button>
        </StackPanel>

        <Button Name="ConvertBtn" Grid.Row="3" Content="Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion process"
                />

        <ProgressBar Name="ProgressBar" Grid.Row="4" Height="10" Margin="0,10,0,0" IsIndeterminate="False"/>
        
        <TextBox Name="LogBox" Grid.Row="5" Margin="0,10,0,0" FontFamily="Consolas" FontSize="12"
                 TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" IsReadOnly="True"/>

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
$UrlBox    = $window.FindName("UrlBox")
$OutBox    = $window.FindName("OutBox")
$BrowseBtn = $window.FindName("BrowseBtn")
$OpenFolderBtn = $window.FindName("OpenFolderBtn")
$ConvertBtn= $window.FindName("ConvertBtn")
$StatusText= $window.FindName("StatusText")
$ProgressBar=$window.FindName("ProgressBar")
$LogBox    = $window.FindName("LogBox")

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

# --- Convert button logic ---
$ConvertBtn.Add_Click({
    $url = $UrlBox.Text.Trim()
    $outdir = $OutBox.Text.Trim()

    $LogBox.Text = "--- Starting Conversion ---`r`n"
    $ProgressBar.IsIndeterminate = $true

    if ([string]::IsNullOrWhiteSpace($url)) {
        $StatusText.Text = "Please enter a URL."
        $StatusText.Foreground = "Red"
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

    # Check for .venv executable (preferred) or standalone script
    $venvExe = Join-Path $scriptDir ".venv\Scripts\html2md.exe"
    $pyScript = Join-Path $scriptDir "html2md.py"
    
    if (Test-Path -LiteralPath $venvExe) {
        $LogBox.AppendText("Found venv executable: $venvExe`r`n")
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell.exe"
        # Run the venv shim directly. It handles paths correctly.
        $psi.Arguments = "-NoExit -Command `"& '$venvExe' --url '$url' --outdir '$outdir' --all-formats`""
        $psi.WorkingDirectory = $scriptDir
        $psi.UseShellExecute = $true
    }
    elseif (Test-Path -LiteralPath $pyScript) {
        $LogBox.AppendText("Found Python script: $pyScript`r`n")
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell.exe"
        $psi.Arguments = "-NoExit -Command `"& $pyCmd '$pyScript' --url '$url' --outdir '$outdir' --all-formats`""
        $psi.WorkingDirectory = $scriptDir
        $psi.UseShellExecute = $true
    }
    else {
        $StatusText.Text = "Error: html2md executable not found."
        $StatusText.Foreground = "Red"
        $LogBox.AppendText("ERROR: Could not find .venv\Scripts\html2md.exe or html2md.py in $scriptDir`r`n")
        $LogBox.AppendText("Have you run setup-html2md.ps1?`r`n")
        $ProgressBar.IsIndeterminate = $false
        return
    }
    
    $LogBox.AppendText("Executing process...`r`n")
    [Diagnostics.Process]::Start($psi) | Out-Null

    $StatusText.Text = "Conversion started in a new console."
    $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
    $ProgressBar.IsIndeterminate = $false
})

# --- Show window ---
$window.ShowDialog() | Out-Null