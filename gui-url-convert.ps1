<#
WPF GUI for html2md
- Auto‑detects STA/MTA
- Relaunches in STA if necessary
- No WinForms (avoids freezes caused by OneDrive/VSCode/ISE)
- Safe for double-click or PowerShell execution
#>

# --- Relaunch in STA mode if needed ---
if ([Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    Write-Host "[INFO] Relaunching in STA mode..."
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-STA -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $psi.UseShellExecute = $true
    [Diagnostics.Process]::Start($psi) | Out-Null
    exit
}

# --- Load WPF assemblies ---
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml

# --- Define XAML UI ---
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        FocusManager.FocusedElement="{Binding ElementName=UrlBox}"
        Title="html2md - Convert URL"
        Height="300" Width="580"
        FocusManager.FocusedElement="{Binding ElementName=UrlBox}"
        WindowStartupLocation="CenterScreen"
        Topmost="True">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <Label Content="_Paste URL:" Target="{Binding ElementName=UrlBox}" FontSize="14"/>
        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10"/>

        <StackPanel Grid.Row="2" Orientation="Horizontal">
            <TextBox Name="OutBox" Width="440" FontSize="14" AutomationProperties.Name="Output Directory"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">Browse…</Button>
        </StackPanel>

        <Button Name="ConvertBtn" Grid.Row="3" Content="Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion process"
                />

        <StatusBar Grid.Row="4" Margin="0,10,0,0">
            <TextBlock Name="StatusText" Text="Ready" Foreground="Gray"/>
        </StatusBar>
    </Grid>
</Window>
"@

# --- Parse XAML ---
$reader = New-Object System.Xml.XmlNodeReader ([xml]$xaml)
$window = [Windows.Markup.XamlReader]::Load($reader)

# --- Get controls ---
$UrlBox    = $window.FindName("UrlBox")
$OutBox    = $window.FindName("OutBox")
$BrowseBtn = $window.FindName("BrowseBtn")
$ConvertBtn= $window.FindName("ConvertBtn")
$StatusText= $window.FindName("StatusText")

# --- Browse button logic ---
$BrowseBtn.Add_Click({
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($dlg.ShowDialog() -eq "OK") {
        $OutBox.Text = $dlg.SelectedPath
    }
})

# --- Convert button logic ---
$ConvertBtn.Add_Click({
    $url = $UrlBox.Text.Trim()
    $outdir = $OutBox.Text.Trim()

    if ([string]::IsNullOrWhiteSpace($url)) {
        $StatusText.Text = "Please enter a URL."
        $StatusText.Foreground = "Red"
        return
    }

    # -- SECURITY CHECK BEGIN --
    # 1. Validate URL is a well-formed absolute URI (HTTP/HTTPS)
    $uri = $null
    if (-not [System.Uri]::TryCreate($url, [System.UriKind]::Absolute, [ref]$uri)) {
        $StatusText.Text = "Error: Invalid URL format."
        $StatusText.Foreground = "Red"
        return
    }
    if ($uri.Scheme -ne 'http' -and $uri.Scheme -ne 'https') {
        $StatusText.Text = "Error: Only http/https URLs are supported."
        $StatusText.Foreground = "Red"
        return
    }

    # 2. Prevent command injection via double quotes
    if ($url.Contains('"') -or $outdir.Contains('"')) {
        $StatusText.Text = "Error: Inputs cannot contain double quotes."
        $StatusText.Foreground = "Red"
        return
    }
    # -- SECURITY CHECK END --

    if (-not (Test-Path $outdir)) {
        try { New-Item -ItemType Directory -Path $outdir -Force | Out-Null }
        catch {}
    }

    $scriptDir = Split-Path -Parent $PSCommandPath
    $bat = Join-Path $scriptDir "run-html2md.bat"

    if (-not (Test-Path $bat)) {
        $StatusText.Text = "Error: run-html2md.bat not found."
        $StatusText.Foreground = "Red"
        return
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "cmd.exe"
    $psi.Arguments = "/c `"$bat`" --url `"$url`" --outdir `"$outdir`" --all-formats"
    $psi.WorkingDirectory = $scriptDir
    $psi.UseShellExecute = $true
    [Diagnostics.Process]::Start($psi) | Out-Null

    $StatusText.Text = "Conversion started in a new console."
    $StatusText.ClearValue([System.Windows.Controls.TextBlock]::ForegroundProperty)
})

# --- Show window ---
$window.ShowDialog() | Out-Null