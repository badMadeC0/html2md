Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml
Add-Type -AssemblyName System.Windows.Forms

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

$xmlDoc = [xml]$xaml
$reader = New-Object System.Xml.XmlNodeReader $xmlDoc
$window = [Windows.Markup.XamlReader]::Load($reader)
Write-Host "XAML Loaded Successfully"
