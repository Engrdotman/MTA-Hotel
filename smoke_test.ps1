# Smoke Test Script - Receptionist Workflow
# This script tests the complete receptionist workflow

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "MTA Hotel - Receptionist Smoke Test" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$baseURL = "http://localhost:8000/api"
$adminEmail = "admin@hotel.com"
$adminPassword = "admin"

# Test 1: Admin Login
Write-Host "[1/15] Testing Admin Login..." -ForegroundColor Yellow
try {
  $loginResponse = Invoke-RestMethod -Uri "$baseURL/auth/login/" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{email=$adminEmail; password=$adminPassword} | ConvertTo-Json) `
    -TimeoutSec 5
  
  $TOKEN = $loginResponse.access
  Write-Host "✅ Admin login successful" -ForegroundColor Green
  Write-Host "   User: $($loginResponse.user.email)"
  Write-Host "   Role: $($loginResponse.user.role.name)"
} catch {
  Write-Host "❌ Admin login failed: $_" -ForegroundColor Red
  exit 1
}

Write-Host ""

# Test 2: Get Dashboard Data
Write-Host "[2/15] Testing Dashboard Metrics..." -ForegroundColor Yellow
try {
  $dashboardResponse = Invoke-RestMethod -Uri "$baseURL/reports/dashboard/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  Write-Host "✅ Dashboard metrics retrieved" -ForegroundColor Green
  Write-Host "   Total Rooms: $($dashboardResponse.total_rooms)"
  Write-Host "   Occupied: $($dashboardResponse.occupied_rooms)"
  Write-Host "   Available: $($dashboardResponse.available_rooms)"
  Write-Host "   Today's Check-ins: $($dashboardResponse.today_check_ins)"
  Write-Host "   Today's Revenue: $($dashboardResponse.today_revenue)"
} catch {
  Write-Host "❌ Dashboard retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Get Rooms
Write-Host "[3/15] Testing Get Rooms..." -ForegroundColor Yellow
try {
  $roomsResponse = Invoke-RestMethod -Uri "$baseURL/rooms/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $rooms = if ($roomsResponse -is [array]) { $roomsResponse } else { @($roomsResponse) }
  Write-Host "✅ Rooms retrieved: $($rooms.Count) rooms" -ForegroundColor Green
  
  if ($rooms.Count -gt 0) {
    Write-Host "   Sample Room: $($rooms[0].room_number), Status: $($rooms[0].status), Rate: $($rooms[0].rate_per_night)"
  }
} catch {
  Write-Host "❌ Get rooms failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Get Guests
Write-Host "[4/15] Testing Get Guests..." -ForegroundColor Yellow
try {
  $guestsResponse = Invoke-RestMethod -Uri "$baseURL/guests/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $guests = if ($guestsResponse -is [array]) { $guestsResponse } else { $guestsResponse.results -or @() }
  Write-Host "✅ Guests retrieved: $($guests.Count) guests" -ForegroundColor Green
  
  if ($guests.Count -gt 0) {
    Write-Host "   Sample Guest: $($guests[0].first_name) $($guests[0].last_name)"
  }
} catch {
  Write-Host "❌ Get guests failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Get Reservations
Write-Host "[5/15] Testing Get Reservations..." -ForegroundColor Yellow
try {
  $reservationsResponse = Invoke-RestMethod -Uri "$baseURL/reservations/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $reservations = if ($reservationsResponse -is [array]) { $reservationsResponse } else { $reservationsResponse.results -or @() }
  Write-Host "✅ Reservations retrieved: $($reservations.Count) reservations" -ForegroundColor Green
  
  if ($reservations.Count -gt 0) {
    $res = $reservations[0]
    Write-Host "   Sample Reservation: Guest $($res.guest), Room $($res.room), Status: $($res.status)"
  }
} catch {
  Write-Host "❌ Get reservations failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 6: Create Guest (Receptionist Task)
Write-Host "[6/15] Testing Create Guest..." -ForegroundColor Yellow
try {
  $guestData = @{
    first_name = "John"
    last_name = "Doe"
    email = "john.doe.$([int](Get-Random))@example.com"
    phone = "234-567-8900"
    address = "123 Main St"
  }
  
  $createGuestResponse = Invoke-RestMethod -Uri "$baseURL/guests/" `
    -Method POST `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -ContentType "application/json" `
    -Body ($guestData | ConvertTo-Json) `
    -TimeoutSec 5
  
  $GUEST_ID = $createGuestResponse.id
  Write-Host "✅ Guest created successfully" -ForegroundColor Green
  Write-Host "   Guest ID: $GUEST_ID"
  Write-Host "   Name: $($createGuestResponse.first_name) $($createGuestResponse.last_name)"
} catch {
  Write-Host "❌ Create guest failed: $_" -ForegroundColor Red
  $GUEST_ID = $null
}

Write-Host ""

# Test 7: Get Room Types
Write-Host "[7/15] Testing Get Room Types..." -ForegroundColor Yellow
try {
  $roomTypesResponse = Invoke-RestMethod -Uri "$baseURL/room-types/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $roomTypes = if ($roomTypesResponse -is [array]) { $roomTypesResponse } else { $roomTypesResponse.results -or @() }
  Write-Host "✅ Room types retrieved: $($roomTypes.Count) types" -ForegroundColor Green
  
  if ($roomTypes.Count -gt 0) {
    Write-Host "   Sample: $($roomTypes[0].name) - Rate: $($roomTypes[0].base_rate)"
  }
} catch {
  Write-Host "❌ Get room types failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 8: Get Available Rooms
Write-Host "[8/15] Testing Get Available Rooms..." -ForegroundColor Yellow
try {
  $availableRoomsResponse = Invoke-RestMethod -Uri "$baseURL/rooms/?status=AVAILABLE" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $availableRooms = if ($availableRoomsResponse -is [array]) { $availableRoomsResponse } else { $availableRoomsResponse.results -or @() }
  Write-Host "✅ Available rooms retrieved: $($availableRooms.Count) available" -ForegroundColor Green
  
  if ($availableRooms.Count -gt 0) {
    $ROOM_ID = $availableRooms[0].id
    Write-Host "   Sample: Room $($availableRooms[0].room_number) - Type: $($availableRooms[0].room_type)"
  } else {
    Write-Host "⚠️  No available rooms found" -ForegroundColor Yellow
  }
} catch {
  Write-Host "❌ Get available rooms failed: $_" -ForegroundColor Red
  $ROOM_ID = $null
}

Write-Host ""

# Test 9: Create Reservation (if guest and room available)
Write-Host "[9/15] Testing Create Reservation..." -ForegroundColor Yellow
if ($GUEST_ID -and $ROOM_ID) {
  try {
    $checkIn = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
    $checkOut = (Get-Date).AddDays(3).ToString("yyyy-MM-dd")
    
    $reservationData = @{
      guest = $GUEST_ID
      room = $ROOM_ID
      check_in_date = $checkIn
      check_out_date = $checkOut
      notes = "Smoke test reservation"
    }
    
    $createReservationResponse = Invoke-RestMethod -Uri "$baseURL/reservations/" `
      -Method POST `
      -Headers @{"Authorization"="Bearer $TOKEN"} `
      -ContentType "application/json" `
      -Body ($reservationData | ConvertTo-Json) `
      -TimeoutSec 5
    
    $RESERVATION_ID = $createReservationResponse.id
    Write-Host "✅ Reservation created successfully" -ForegroundColor Green
    Write-Host "   Reservation ID: $RESERVATION_ID"
    Write-Host "   Check-in: $checkIn"
    Write-Host "   Check-out: $checkOut"
  } catch {
    Write-Host "❌ Create reservation failed: $_" -ForegroundColor Red
    $RESERVATION_ID = $null
  }
} else {
  Write-Host "⚠️  Skipped: No guest or room available" -ForegroundColor Yellow
  $RESERVATION_ID = $null
}

Write-Host ""

# Test 10: Check-in Guest
Write-Host "[10/15] Testing Guest Check-in..." -ForegroundColor Yellow
if ($RESERVATION_ID) {
  try {
    $checkInResponse = Invoke-RestMethod -Uri "$baseURL/reservations/$RESERVATION_ID/check-in/" `
      -Method POST `
      -Headers @{"Authorization"="Bearer $TOKEN"} `
      -ContentType "application/json" `
      -Body '{}' `
      -TimeoutSec 5
    
    $STAY_ID = $checkInResponse.stay_id
    Write-Host "✅ Check-in successful" -ForegroundColor Green
    Write-Host "   Stay ID: $STAY_ID"
    Write-Host "   Status: $($checkInResponse.status)"
  } catch {
    Write-Host "❌ Check-in failed: $_" -ForegroundColor Red
    $STAY_ID = $null
  }
} else {
  Write-Host "⚠️  Skipped: No reservation available" -ForegroundColor Yellow
  $STAY_ID = $null
}

Write-Host ""

# Test 11: Get Invoices
Write-Host "[11/15] Testing Get Invoices..." -ForegroundColor Yellow
try {
  $invoicesResponse = Invoke-RestMethod -Uri "$baseURL/billing/invoices/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  $invoices = if ($invoicesResponse -is [array]) { $invoicesResponse } else { $invoicesResponse.results -or @() }
  Write-Host "✅ Invoices retrieved: $($invoices.Count) invoices" -ForegroundColor Green
  
  if ($invoices.Count -gt 0) {
    Write-Host "   Sample: Invoice $($invoices[0].invoice_number) - Total: $($invoices[0].total_amount)"
  }
} catch {
  Write-Host "❌ Get invoices failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 12: Get Reports
Write-Host "[12/15] Testing Get Reports..." -ForegroundColor Yellow
try {
  $occupancyResponse = Invoke-RestMethod -Uri "$baseURL/reports/occupancy/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  Write-Host "✅ Occupancy report retrieved" -ForegroundColor Green
  Write-Host "   Occupied: $($occupancyResponse.occupied)"
  Write-Host "   Available: $($occupancyResponse.available)"
  Write-Host "   Reserved: $($occupancyResponse.reserved)"
  Write-Host "   Occupancy Rate: $($occupancyResponse.occupancy_rate)%"
} catch {
  Write-Host "❌ Get reports failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 13: Get Revenue Report
Write-Host "[13/15] Testing Revenue Report..." -ForegroundColor Yellow
try {
  $revenueResponse = Invoke-RestMethod -Uri "$baseURL/reports/revenue/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  Write-Host "✅ Revenue report retrieved" -ForegroundColor Green
  Write-Host "   Total Revenue: $($revenueResponse.total_revenue)"
  Write-Host "   Cash: $($revenueResponse.cash)"
  Write-Host "   POS: $($revenueResponse.pos)"
  Write-Host "   Bank Transfer: $($revenueResponse.bank_transfer)"
} catch {
  Write-Host "❌ Revenue report failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 14: Get Outstanding Report
Write-Host "[14/15] Testing Outstanding Balances..." -ForegroundColor Yellow
try {
  $outstandingResponse = Invoke-RestMethod -Uri "$baseURL/reports/outstanding/" `
    -Method GET `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -TimeoutSec 5
  
  Write-Host "✅ Outstanding report retrieved" -ForegroundColor Green
  Write-Host "   Total Outstanding: $($outstandingResponse.total_outstanding)"
  Write-Host "   Unpaid Invoices: $($outstandingResponse.unpaid_invoices)"
  Write-Host "   Partially Paid: $($outstandingResponse.partially_paid_invoices)"
} catch {
  Write-Host "❌ Outstanding report failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 15: Logout
Write-Host "[15/15] Testing Logout..." -ForegroundColor Yellow
try {
  $logoutData = @{
    refresh = $loginResponse.refresh
  }
  
  $logoutResponse = Invoke-RestMethod -Uri "$baseURL/auth/logout/" `
    -Method POST `
    -Headers @{"Authorization"="Bearer $TOKEN"} `
    -ContentType "application/json" `
    -Body ($logoutData | ConvertTo-Json) `
    -TimeoutSec 5
  
  Write-Host "✅ Logout successful" -ForegroundColor Green
} catch {
  Write-Host "❌ Logout failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Smoke Test Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
