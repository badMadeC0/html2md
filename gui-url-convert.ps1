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
        Title="html2md - Convert URL"
        Height="280" Width="580"
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

        <TextBlock Text="Paste URL:" FontSize="14"/>
        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10"/>

        <StackPanel Grid.Row="2" Orientation="Horizontal">
            <TextBox Name="OutBox" Width="440" FontSize="14" Text="./out"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0">Browse…</Button>
        </StackPanel>

        <Button Name="ConvertBtn" Grid.Row="3" Content="Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                />

        <StatusBar Grid.Row="5" Margin="0,10,0,0">
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

if ($null -eq $StatusText) {
    throw "UI element 'StatusText' was not found in XAML."
}

$resetStatusAction = {
    $StatusText.Text = "Ready"
    $StatusText.Foreground = "Gray"
}
$UrlBox.Add_TextChanged($resetStatusAction)
$OutBox.Add_TextChanged($resetStatusAction)

# --- Browse button logic ---
$BrowseBtn.Add_Click({
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml
Add-Type -AssemblyName System.Windows.Forms

# --- Convert button logic ---
$ConvertBtn.Add_Click({
    $url = $UrlBox.Text.Trim()
    $outdir = $OutBox.Text.Trim()

    if ([string]::IsNullOrWhiteSpace($url)) {
        $StatusText.Text = "Please enter a URL."
        $StatusText.Foreground = "Red"
        return
    }

    # --- Security Validation Start ---
    if ($outdir.Contains('"')) {
        [System.Windows.MessageBox]::Show("Output directory path cannot contain double quotes.", "Invalid Path", "OK", "Error") | Out-Null
        return
    }

    try {
        $uri = New-Object System.Uri($url)
        if ($uri.Scheme -ne 'http' -and $uri.Scheme -ne 'https') {
            [System.Windows.MessageBox]::Show("Only HTTP and HTTPS URLs are supported.", "Invalid URL Scheme", "OK", "Warning") | Out-Null
            return
        }
        $url = $uri.AbsoluteUri
    } catch {
        [System.Windows.MessageBox]::Show("Invalid URL format.", "Invalid URL", "OK", "Error") | Out-Null
        return
    }
    # --- Security Validation End ---

    # Input Validation
    try {
        $uri = [System.Uri]$url
        if ($uri.Scheme -ne 'http' -and $uri.Scheme -ne 'https') {
             [System.Windows.MessageBox]::Show("Only HTTP and HTTPS URLs are supported.","Invalid Protocol","OK","Error") | Out-Null
             return
        }
        $url = $uri.AbsoluteUri # Canonicalize URL
    } catch {
        [System.Windows.MessageBox]::Show("Invalid URL format.","Error","OK","Error") | Out-Null
        return
    }

    if ($outdir.Contains('"')) {
        [System.Windows.MessageBox]::Show("Output directory path cannot contain double quotes.","Invalid Path","OK","Error") | Out-Null
        return
    }

    if (-not (Test-Path -LiteralPath $outdir)) {
        try {
            New-Item -ItemType Directory -LiteralPath $outdir -Force | Out-Null
        } catch {
            [System.Windows.MessageBox]::Show("Failed to create output directory.","Error","OK","Error") | Out-Null
            return
        }
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

    $StatusText.Text = "Conversion launched in external console."
    $StatusText.Foreground = "Black"
})

# --- Show window ---
$window.ShowDialog() | Out-Null
