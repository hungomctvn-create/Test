# Script chuyển file khắc phục lên Raspberry Pi
# Sử dụng SCP để upload các file cần thiết

param(
    [Parameter(Mandatory=$true)]
    [string]$RaspberryPiIP,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [string]$RemotePath = "/home/pi"
)

Write-Host "=== CHUYỂN FILE KHẮC PHỤC LÊN RASPBERRY PI ===" -ForegroundColor Green
Write-Host "Raspberry Pi IP: $RaspberryPiIP" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow
Write-Host "Remote Path: $RemotePath" -ForegroundColor Yellow
Write-Host ""

# Danh sách file cần chuyển
$FilesToUpload = @(
    "fix_raspberry_pi.sh",
    "requirements.txt", 
    "test_installation.py",
    "yolo_opencv_simple.py",
    "Nhan_dang_nguoi_yolo"
)

Write-Host "Bắt đầu chuyển file khắc phục..." -ForegroundColor Cyan

foreach ($file in $FilesToUpload) {
    $localFile = Join-Path $PSScriptRoot $file
    
    if (Test-Path $localFile) {
        Write-Host "Đang chuyển: $file" -ForegroundColor Yellow
        
        try {
            $scpCommand = "scp `"$localFile`" ${Username}@${RaspberryPiIP}:${RemotePath}/"
            Write-Host "Executing: $scpCommand" -ForegroundColor Gray
            Invoke-Expression $scpCommand
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Đã chuyển thành công: $file" -ForegroundColor Green
            } else {
                Write-Host "✗ Lỗi khi chuyển: $file" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ Lỗi: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠ Không tìm thấy file: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== HƯỚNG DẪN TIẾP THEO ===" -ForegroundColor Green
Write-Host "1. SSH vào Raspberry Pi:" -ForegroundColor White
Write-Host "   ssh ${Username}@${RaspberryPiIP}" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Chạy script khắc phục:" -ForegroundColor White
Write-Host "   chmod +x fix_raspberry_pi.sh" -ForegroundColor Gray
Write-Host "   bash fix_raspberry_pi.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Kiểm tra kết quả:" -ForegroundColor White
Write-Host "   python3 test_installation.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Chạy ứng dụng đã sửa:" -ForegroundColor White
Write-Host "   python3 yolo_opencv_simple.py" -ForegroundColor Gray
Write-Host "   # hoặc" -ForegroundColor Gray
Write-Host "   python3 Nhan_dang_nguoi_yolo" -ForegroundColor Gray