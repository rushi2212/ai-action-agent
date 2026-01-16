# Installation and Setup Script
# Run this in PowerShell from the project root directory

Write-Host "🚀 AI Action Agent - Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Expected structure: backend/ and frontend/ folders" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n📦 Step 1: Installing Backend Dependencies" -ForegroundColor Green
Set-Location backend

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}

# Install Python packages
Write-Host "`nInstalling Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python packages" -ForegroundColor Red
    exit 1
}

# Install Playwright browsers
Write-Host "`n🌐 Step 2: Installing Playwright Browsers" -ForegroundColor Green
playwright install chromium

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Playwright browsers installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Playwright browsers" -ForegroundColor Red
    exit 1
}

# Check for GROQ API key
Write-Host "`n🔑 Step 3: Checking GROQ API Key" -ForegroundColor Green
if ($env:GROQ_API_KEY) {
    Write-Host "✓ GROQ_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  GROQ_API_KEY is not set" -ForegroundColor Yellow
    Write-Host "   Please set it before running the server:" -ForegroundColor Yellow
    Write-Host '   $env:GROQ_API_KEY="your-api-key-here"' -ForegroundColor Cyan
}

# Go to frontend
Set-Location ../frontend

Write-Host "`n📦 Step 4: Installing Frontend Dependencies" -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Install npm packages
Write-Host "`nInstalling npm packages..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ npm packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to install npm packages (you can skip this if you only need the backend)" -ForegroundColor Yellow
}

# Return to project root
Set-Location ..

Write-Host "`n✅ Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Set your GROQ API key:" -ForegroundColor White
Write-Host '   $env:GROQ_API_KEY="your-api-key-here"' -ForegroundColor Yellow
Write-Host "`n2. Start the backend server:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Yellow
Write-Host "   uvicorn main:app --reload" -ForegroundColor Yellow
Write-Host "`n3. (Optional) Start the frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Yellow
Write-Host "   npm run dev" -ForegroundColor Yellow
Write-Host "`n4. Test the improvements:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Yellow
Write-Host "   python test_agent.py" -ForegroundColor Yellow
Write-Host "`n📚 Read QUICK_START.md for usage examples!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
