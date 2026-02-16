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
        Height="250" Width="580"
        WindowStartupLocation="CenterScreen"
        Topmost="True">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <Label Target="{Binding ElementName=UrlBox}" FontSize="14" Content="_Paste URL:"/>
        <TextBox Name="UrlBox" Grid.Row="1" FontSize="14" Margin="0,5,0,10"
                 AutomationProperties.Name="Paste URL"
                 ToolTip="Enter the URL you want to convert"/>

        <Label Grid.Row="2" Target="{Binding ElementName=OutBox}" FontSize="14" Content="_Output Directory:"/>
        <StackPanel Grid.Row="3" Orientation="Horizontal" Margin="0,5,0,10">
            <TextBox Name="OutBox" Width="440" FontSize="14" Text="./out"
                     AutomationProperties.Name="Output Directory"
                     ToolTip="The directory where output files will be saved"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0"
                    Content="_Browse…" ToolTip="Browse for output directory"/>
        </StackPanel>

        <Button Name="ConvertBtn" Grid.Row="4" Content="_Convert (All Formats)"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion for all supported formats"
                />
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

# --- Browse button logic ---
$BrowseBtn.Add_Click({
    $shell = $null
    $folder = $null
    $folderItem = $null
    try {
        $shell = New-Object -ComObject Shell.Application
        # BrowseForFolder: hwnd=window handle, title, options=0, rootFolder=0 (Desktop)
        $interopHelper = New-Object System.Windows.Interop.WindowInteropHelper($window)
        $hwnd = $interopHelper.Handle
        $folder = $shell.BrowseForFolder($hwnd, "Select output directory", 0, 0)
        if ($folder) {
            $folderItem = $folder.Self
            $OutBox.Text = $folderItem.Path
        }
    } finally {
        if ($folderItem) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($folderItem) | Out-Null
            $folderItem = $null
        }
        if ($folder) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($folder) | Out-Null
            $folder = $null
        }
        if ($shell) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($shell) | Out-Null
            $shell = $null
        }
    }
})

# --- Convert button logic ---
$ConvertBtn.Add_Click({
    $url = $UrlBox.Text.Trim()
    $outdir = $OutBox.Text.Trim()

    if ([string]::IsNullOrWhiteSpace($url)) {
        [System.Windows.MessageBox]::Show("Please enter a URL.","Missing URL","OK","Warning") | Out-Null
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

    if (-not (Test-Path $outdir)) {
        try { New-Item -ItemType Directory -Path $outdir -Force | Out-Null }
        catch {}
    }

    $scriptDir = Split-Path -Parent $PSCommandPath
    $bat = Join-Path $scriptDir "run-html2md.bat"

    if (-not (Test-Path $bat)) {
        [System.Windows.MessageBox]::Show("run-html2md.bat not found.","Error","OK","Error") | Out-Null
        return
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "cmd.exe"
    $psi.Arguments = "/c `"$bat`" --url `"$url`" --outdir `"$outdir`" --all-formats"
    $psi.WorkingDirectory = $scriptDir
    $psi.UseShellExecute = $true
    [Diagnostics.Process]::Start($psi) | Out-Null

    [System.Windows.MessageBox]::Show("Conversion started in a new console.","Launched") | Out-Null
})

# --- Show window ---
$window.ShowDialog() | Out-Null
