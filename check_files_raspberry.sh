#!/bin/bash

echo "🔍 KIỂM TRA VÀ SỬA TÊN FILE TRÊN RASPBERRY PI"
echo "============================================="

# Kiểm tra thư mục hiện tại
echo "📁 Thư mục hiện tại:"
pwd
echo ""

echo "📋 Danh sách tất cả file Python:"
ls -la *.py 2>/dev/null || echo "Không có file .py nào"
echo ""

echo "📋 Danh sách tất cả file (không có extension):"
ls -la | grep -v "\.py$" | grep -v "\.sh$" | grep -v "\.md$" | grep -v "\.txt$"
echo ""

# Tìm file chính
echo "🔍 Tìm file chương trình chính..."
if [ -f "Nhan_dang_nguoi_yolo.py" ]; then
    echo "✅ Tìm thấy: Nhan_dang_nguoi_yolo.py"
elif [ -f "nhan_dang_nguoi_yolo.py" ]; then
    echo "✅ Tìm thấy: nhan_dang_nguoi_yolo.py"
elif [ -f "Nhan_dang_nguoi_yolo" ]; then
    echo "⚠️  Tìm thấy file không có extension: Nhan_dang_nguoi_yolo"
    echo "🔧 Đổi tên thành .py..."
    mv "Nhan_dang_nguoi_yolo" "Nhan_dang_nguoi_yolo.py"
    echo "✅ Đã đổi tên thành: Nhan_dang_nguoi_yolo.py"
elif [ -f "nhan_dang_nguoi_yolo" ]; then
    echo "⚠️  Tìm thấy file không có extension: nhan_dang_nguoi_yolo"
    echo "🔧 Đổi tên thành .py..."
    mv "nhan_dang_nguoi_yolo" "nhan_dang_nguoi_yolo.py"
    echo "✅ Đã đổi tên thành: nhan_dang_nguoi_yolo.py"
else
    echo "❌ Không tìm thấy file chương trình chính!"
    echo "💡 Các file có thể liên quan:"
    ls -la *yolo* 2>/dev/null || echo "Không có file nào chứa 'yolo'"
    ls -la *nhan* 2>/dev/null || echo "Không có file nào chứa 'nhan'"
fi

echo ""
echo "🔧 Sửa quyền thực thi cho tất cả file .py:"
chmod +x *.py 2>/dev/null
echo "✅ Đã cấp quyền thực thi"

echo ""
echo "📋 Danh sách file sau khi sửa:"
ls -la *.py 2>/dev/null || echo "Vẫn không có file .py nào"

echo ""
echo "🧪 Test chạy file chính:"
if [ -f "Nhan_dang_nguoi_yolo.py" ]; then
    echo "python3 Nhan_dang_nguoi_yolo.py"
    python3 -c "
import sys
try:
    with open('Nhan_dang_nguoi_yolo.py', 'r') as f:
        print('✅ File có thể đọc được')
        lines = len(f.readlines())
        print(f'✅ File có {lines} dòng')
except Exception as e:
    print(f'❌ Lỗi đọc file: {e}')
"
elif [ -f "nhan_dang_nguoi_yolo.py" ]; then
    echo "python3 nhan_dang_nguoi_yolo.py"
    python3 -c "
import sys
try:
    with open('nhan_dang_nguoi_yolo.py', 'r') as f:
        print('✅ File có thể đọc được')
        lines = len(f.readlines())
        print(f'✅ File có {lines} dòng')
except Exception as e:
    print(f'❌ Lỗi đọc file: {e}')
"
else
    echo "❌ Vẫn không tìm thấy file để test"
fi

echo ""
echo "💡 HƯỚNG DẪN:"
echo "1. Nếu file đã OK, chạy: python3 Nhan_dang_nguoi_yolo.py"
echo "2. Nếu vẫn lỗi, kiểm tra encoding: file Nhan_dang_nguoi_yolo.py"
echo "3. Nếu cần upload lại: scp từ Windows"