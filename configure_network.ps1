# Spam Detector Network Configuration Script for Windows
# Run as Administrator for full functionality

param(
    [int]$Port = 5001,
    [string]$Host = "127.0.0.1"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Spam Detector Network Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some network configurations may fail" -ForegroundColor Yellow
    Write-Host "Consider running PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host ""
}

# Function to add firewall rule
function Add-FirewallRule {
    param($Port)
    
    try {
        $ruleName = "Spam Detector Flask App Port $Port"
        
        # Check if rule exists
        $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        
        if ($existingRule) {
            Write-Host "Firewall rule already exists for port $Port" -ForegroundColor Green
        } else {
            # Add inbound rule
            New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Profile Domain,Private,Public
            Write-Host "Added firewall exception for port $Port" -ForegroundColor Green
        }
        return $true
    } catch {
        Write-Host "Could not add firewall rule: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try running as Administrator" -ForegroundColor Yellow
        return $false
    }
}

# Function to kill processes on port
function Stop-ProcessOnPort {
    param($Port)
    
    try {
        $connections = netstat -ano | Select-String ":$Port "
        
        if ($connections) {
            Write-Host "Found processes using port $Port" -ForegroundColor Yellow
            
            foreach ($connection in $connections) {
                $parts = $connection.ToString().Trim() -split '\s+'
                if ($parts.Length -ge 5) {
                    $pid = $parts[-1]
                    if ($pid -match '^\d+$') {
                        try {
                            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                            if ($process) {
                                Write-Host "Stopping process $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                                Stop-Process -Id $pid -Force
                            }
                        } catch {
                            Write-Host "Could not stop process $pid" -ForegroundColor Red
                        }
                    }
                }
            }
        } else {
            Write-Host "No processes found using port $Port" -ForegroundColor Green
        }
    } catch {
        Write-Host "Error checking port usage: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to test network connectivity
function Test-NetworkSetup {
    param($Host, $Port)
    
    Write-Host "Testing network configuration..." -ForegroundColor Cyan
    
    # Test localhost resolution
    try {
        $localhost = [System.Net.Dns]::GetHostEntry("localhost")
        Write-Host "localhost resolves to: $($localhost.AddressList[0])" -ForegroundColor Green
    } catch {
        Write-Host "localhost resolution failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test port availability
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect($Host, $Port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne(1000, $false)
        
        if ($tcpClient.Connected) {
            Write-Host "Port $Port is already in use" -ForegroundColor Red
            $tcpClient.Close()
            return $false
        } else {
            Write-Host "Port $Port is available" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "Port $Port is available" -ForegroundColor Green
        return $true
    }
}

# Function to configure Windows Defender exclusions
function Add-DefenderExclusion {
    try {
        $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($pythonPath) {
            $pythonDir = Split-Path $pythonPath -Parent
            Add-MpPreference -ExclusionPath $pythonDir -ErrorAction SilentlyContinue
            Write-Host "Added Windows Defender exclusion for Python directory" -ForegroundColor Green
        }
        
        $currentDir = Get-Location
        Add-MpPreference -ExclusionPath $currentDir.Path -ErrorAction SilentlyContinue
        Write-Host "Added Windows Defender exclusion for project directory" -ForegroundColor Green
        
        return $true
    } catch {
        Write-Host "Could not add Windows Defender exclusions: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "You may need to add them manually" -ForegroundColor Yellow
        return $false
    }
}

# Main configuration process
Write-Host "Step 1: Checking network connectivity" -ForegroundColor Cyan
$networkOk = Test-NetworkSetup -Host $Host -Port $Port

Write-Host ""
Write-Host "Step 2: Stopping conflicting processes" -ForegroundColor Cyan
Stop-ProcessOnPort -Port $Port

Write-Host ""
Write-Host "Step 3: Configuring Windows Firewall" -ForegroundColor Cyan
$firewallOk = Add-FirewallRule -Port $Port

Write-Host ""
Write-Host "Step 4: Configuring Windows Defender" -ForegroundColor Cyan
$defenderOk = Add-DefenderExclusion

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Configuration Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($networkOk -and $firewallOk) {
    Write-Host "Network configuration completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the server with:" -ForegroundColor White
    Write-Host "  python start_server.py" -ForegroundColor Yellow
    Write-Host "  or" -ForegroundColor White
    Write-Host "  start_server.bat" -ForegroundColor Yellow
} else {
    Write-Host "Some configuration steps failed" -ForegroundColor Red
    Write-Host "Check the messages above and try running as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Alternative solutions:" -ForegroundColor White
Write-Host "1. Try different port: python start_server.py --port 8000" -ForegroundColor Gray
Write-Host "2. Use all interfaces: python start_server.py --host 0.0.0.0" -ForegroundColor Gray
Write-Host "3. Run diagnostics: python diagnose_network.py" -ForegroundColor Gray

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
