Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml
Add-Type -AssemblyName System.Windows.Forms

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        Title="html2md - Convert URL"
        Height="450" Width="580"
        WindowStartupLocation="CenterScreen">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <StackPanel Grid.Row="2" Orientation="Horizontal">
            <Label Content="_Output:" Target="{Binding ElementName=OutBox}" FontSize="14" VerticalAlignment="Center"/>
            <TextBox Name="OutBox" Width="275" FontSize="14" AutomationProperties.Name="Output Directory" VerticalContentAlignment="Center" ToolTip="Directory where files will be saved"/>
            <Button Name="BrowseBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">_Browse...</Button>
            <Button Name="OpenFolderBtn" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">_Open Folder</Button>
        </StackPanel>
    </Grid>
</Window>
"@

$xmlDoc = [xml]$xaml
$reader = New-Object System.Xml.XmlNodeReader $xmlDoc
$window = [Windows.Markup.XamlReader]::Load($reader)

# We can't actually show the dialog in a headless sandbox, but we can verify it parses successfully.
Write-Host "XAML parsed successfully"
