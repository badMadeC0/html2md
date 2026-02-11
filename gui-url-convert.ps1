
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$form = New-Object System.Windows.Forms.Form
$form.Text = 'html2md - Convert URL'
$form.Size = New-Object System.Drawing.Size(560,180)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $true
$label = New-Object System.Windows.Forms.Label
$label.Text = 'Paste a URL:'
$label.AutoSize = $true
$label.Location = New-Object System.Drawing.Point(12,15)
$form.Controls.Add($label)
$text = New-Object System.Windows.Forms.TextBox
$text.Size = New-Object System.Drawing.Size(520, 22)
$text.Location = New-Object System.Drawing.Point(12, 36)
$text.Anchor = 'Top,Left,Right'
$form.Controls.Add($text)
$labelOut = New-Object System.Windows.Forms.Label
$labelOut.Text = 'Output folder:'
$labelOut.AutoSize = $true
$labelOut.Location = New-Object System.Drawing.Point(12,70)
$form.Controls.Add($labelOut)
$outBox = New-Object System.Windows.Forms.TextBox
$outBox.Size = New-Object System.Drawing.Size(440,22)
$outBox.Location = New-Object System.Drawing.Point(12, 90)
$outBox.Text = '.\out'
$outBox.Anchor = 'Top,Left,Right'
$form.Controls.Add($outBox)
$browse = New-Object System.Windows.Forms.Button
$browse.Text = 'Browse...'
$browse.Size = New-Object System.Drawing.Size(80,24)
$browse.Location = New-Object System.Drawing.Point(472, 88)
$browse.Add_Click({ $dlg = New-Object System.Windows.Forms.FolderBrowserDialog; if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $outBox.Text = $dlg.SelectedPath } })
$form.Controls.Add($browse)
$btn = New-Object System.Windows.Forms.Button
$btn.Text = 'Convert (All Formats)'
$btn.Size = New-Object System.Drawing.Size(160,28)
$btn.Location = New-Object System.Drawing.Point(372, 120)
$btn.Anchor = 'Bottom,Right'
$btn.Add_Click({ $u = $text.Text.Trim(); $outDir = $outBox.Text.Trim(); if ([string]::IsNullOrWhiteSpace($u)) { [System.Windows.Forms.MessageBox]::Show('Please paste a URL.','Missing URL',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null; return } if (-not (Test-Path $outDir)) { try { New-Item -ItemType Directory -Path $outDir -Force | Out-Null } catch {} } $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path; $bat = Join-Path $scriptDir 'run-html2md.bat'; if (-not (Test-Path $bat)) { [System.Windows.Forms.MessageBox]::Show('run-html2md.bat not found in repo root.','Missing launcher',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null; return } $psi = New-Object System.Diagnostics.ProcessStartInfo; $psi.FileName = 'cmd.exe'; $psi.Arguments = "/c `"$bat`" --url `"$u`" --outdir `"$outDir`" --all-formats"; $psi.WorkingDirectory = $scriptDir; $psi.UseShellExecute = $true; [System.Diagnostics.Process]::Start($psi) | Out-Null; [System.Windows.Forms.MessageBox]::Show('Started conversion in a new console.','Launched',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null })
$form.Controls.Add($btn)
[void]$form.ShowDialog()
