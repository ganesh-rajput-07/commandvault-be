#!/bin/bash

# Test Runner Script for CommandVault

echo "🧪 CommandVault Test Runner"
echo "============================"
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Run tests
echo ""
echo "Running tests..."
echo ""

if [ "$1" == "coverage" ]; then
    # Run with coverage
    echo "📊 Running tests with coverage..."
    coverage run --source='.' manage.py test --verbosity=2
    echo ""
    echo "📈 Coverage Report:"
    coverage report
    echo ""
    echo "💡 For detailed HTML report, run: coverage html"
    echo "   Then open: htmlcov/index.html"
elif [ "$1" == "UserAUth" ]; then
    # Run only auth tests
    echo "🔐 Running authentication tests..."
    python manage.py test UserAUth --verbosity=2
elif [ "$1" == "vault" ]; then
    # Run only vault tests
    echo "📦 Running vault tests..."
    python manage.py test vault --verbosity=2
else
    # Run all tests
    echo "🚀 Running all tests..."
    python manage.py test --verbosity=2
fi

echo ""
echo "✅ Test run complete!"
