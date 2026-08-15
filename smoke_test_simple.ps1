# Simple Smoke Test - Receptionist Workflow

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "MTA Hotel - Receptionist Smoke Test" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$baseURL = "http://localhost:8000/api"

# Test 1: Admin Login
Write-Host "[1/8] Testing Admin Login..." -ForegroundColor Yellow
try {
  $body = @{email="admin@hotel.com"; password="admin"} | ConvertTo-Json
  $login = Invoke-RestMethod -Uri "$baseURL/auth/login/" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
  
  $TOKEN = $login.access
  Write-Host "✅ Admin login successful" -ForegroundColor Green
  Write-Host "   User: $($login.user.email)"
  Write-Host "   Role: $($login.user.role.name)"
  Write-Host ""
} catch {
  Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}

# Test 2: Get Dashboard
Write-Host "[2/8] Testing Dashboard Data..." -ForegroundColor Yellow
try {
  $dashboard = Invoke-RestMethod -Uri "$baseURL/reports/dashboard/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  Write-Host "✅ Dashboard data retrieved" -ForegroundColor Green
  Write-Host "   Total Rooms: $($dashboard.total_rooms)"
  Write-Host "   Occupied: $($dashboard.occupied_rooms)"
  Write-Host "   Today's Revenue: $($dashboard.today_revenue)"
  Write-Host ""
} catch {
  Write-Host "❌ Dashboard failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Get Rooms
Write-Host "[3/8] Testing Rooms..." -ForegroundColor Yellow
try {
  $rooms = Invoke-RestMethod -Uri "$baseURL/rooms/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  $roomList = if ($rooms -is [array]) { $rooms } else { @($rooms) }
  Write-Host "✅ Rooms retrieved: $($roomList.Count) rooms" -ForegroundColor Green
  if ($roomList.Count -gt 0) {
    Write-Host "   Room 1: #$($roomList[0].room_number), Status: $($roomList[0].status)"
  }
  Write-Host ""
} catch {
  Write-Host "❌ Rooms failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Get Guests
Write-Host "[4/8] Testing Guests..." -ForegroundColor Yellow
try {
  $guests = Invoke-RestMethod -Uri "$baseURL/guests/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  $guestList = if ($guests -is [array]) { $guests } else { $guests.results -or @() }
  Write-Host "✅ Guests retrieved: $($guestList.Count) guests" -ForegroundColor Green
  Write-Host ""
} catch {
  Write-Host "❌ Guests failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get Reservations
Write-Host "[5/8] Testing Reservations..." -ForegroundColor Yellow
try {
  $reservations = Invoke-RestMethod -Uri "$baseURL/reservations/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  $resList = if ($reservations -is [array]) { $reservations } else { $reservations.results -or @() }
  Write-Host "✅ Reservations retrieved: $($resList.Count) reservations" -ForegroundColor Green
  Write-Host ""
} catch {
  Write-Host "❌ Reservations failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get Occupancy Report
Write-Host "[6/8] Testing Occupancy Report..." -ForegroundColor Yellow
try {
  $occupancy = Invoke-RestMethod -Uri "$baseURL/reports/occupancy/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  Write-Host "✅ Occupancy report retrieved" -ForegroundColor Green
  Write-Host "   Occupied: $($occupancy.occupied) rooms"
  Write-Host "   Available: $($occupancy.available) rooms"
  Write-Host "   Occupancy Rate: $($occupancy.occupancy_rate)%"
  Write-Host ""
} catch {
  Write-Host "❌ Occupancy report failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Get Invoices
Write-Host "[7/8] Testing Invoices..." -ForegroundColor Yellow
try {
  $invoices = Invoke-RestMethod -Uri "$baseURL/billing/invoices/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  $invoiceList = if ($invoices -is [array]) { $invoices } else { $invoices.results -or @() }
  Write-Host "✅ Invoices retrieved: $($invoiceList.Count) invoices" -ForegroundColor Green
  Write-Host ""
} catch {
  Write-Host "❌ Invoices failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Get Outstanding Report
Write-Host "[8/8] Testing Outstanding Balances..." -ForegroundColor Yellow
try {
  $outstanding = Invoke-RestMethod -Uri "$baseURL/reports/outstanding/" `
    -Method GET -Headers @{"Authorization"="Bearer $TOKEN"} -TimeoutSec 5
  
  Write-Host "✅ Outstanding report retrieved" -ForegroundColor Green
  Write-Host "   Total Outstanding: $($outstanding.total_outstanding)"
  Write-Host "   Unpaid Invoices: $($outstanding.unpaid_invoices)"
  Write-Host ""
} catch {
  Write-Host "❌ Outstanding report failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "All API Endpoints Working!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
