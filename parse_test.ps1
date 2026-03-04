Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        Title="html2md - Convert URL">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <Grid Grid.Row="2">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Label Grid.Column="0" Content="O_utput:" Target="{Binding ElementName=OutBox}" FontSize="14" VerticalAlignment="Center" Margin="0,0,5,0"/>
            <TextBox Name="OutBox" Grid.Column="1" FontSize="14" Height="28" VerticalContentAlignment="Center" AutomationProperties.Name="Output Directory" ToolTip="Directory where files will be saved"/>
            <Button Name="BrowseBtn" Grid.Column="2" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Select output folder">_Browse...</Button>
            <Button Name="OpenFolderBtn" Grid.Column="3" Width="90" Height="28" Margin="10,0,0,0" ToolTip="Open output folder">_Open Folder</Button>
        </Grid>

        <StackPanel Grid.Row="3" Orientation="Horizontal" VerticalAlignment="Center" HorizontalAlignment="Left" Margin="0,15,0,0">
            <CheckBox Name="WholePageChk" Content="Convert _Whole Page"
                      VerticalAlignment="Center" ToolTip="If checked, includes headers and footers. Default is main content only."/>
            <CheckBox Name="AllFormatsChk" Content="Generate _All Formats (md, txt, pdf)" IsChecked="False"
                      VerticalAlignment="Center" Margin="15,0,0,0" ToolTip="If checked, creates .md, .txt, and .pdf files. Uncheck if the converter doesn't support this."/>
        </StackPanel>

        <Button Name="ConvertBtn" Grid.Row="3" Content="_Convert"
                Height="35" HorizontalAlignment="Right" Width="180" Margin="0,15,0,0"
                ToolTip="Start conversion process"/>
    </Grid>
</Window>
"@

$xmlDoc = [xml]$xaml
$reader = New-Object System.Xml.XmlNodeReader $xmlDoc
try {
    $window = [Windows.Markup.XamlReader]::Load($reader)
    Write-Host "XAML parsed successfully"
} catch {
    Write-Host "Error parsing XAML: $_"
}
