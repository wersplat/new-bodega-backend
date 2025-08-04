#!/bin/bash

# NBA 2K Global Rankings Backend - Development Setup Script

set -e

echo "🚀 Setting up NBA 2K Global Rankings Backend development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        REQUIRED_VERSION="3.9"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your actual configuration values"
    else
        print_warning "Environment file already exists"
    fi
}

# Install pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found. Install with: pip install pre-commit"
    fi
}

# Run initial tests
run_tests() {
    print_status "Running initial tests..."
    source venv/bin/activate
    if pytest --version &> /dev/null; then
        pytest tests/ -v --tb=short
        print_success "Tests completed"
    else
        print_warning "pytest not available. Tests skipped."
    fi
}

# Check code formatting
check_formatting() {
    print_status "Checking code formatting..."
    source venv/bin/activate
    
    if command -v black &> /dev/null; then
        black --check app/ main.py
        print_success "Code formatting check passed"
    else
        print_warning "black not available. Formatting check skipped."
    fi
    
    if command -v isort &> /dev/null; then
        isort --check-only app/ main.py
        print_success "Import sorting check passed"
    else
        print_warning "isort not available. Import sorting check skipped."
    fi
}

# Main setup function
main() {
    print_status "Starting development setup..."
    
    check_python
    create_venv
    install_dependencies
    setup_env
    setup_pre_commit
    check_formatting
    run_tests
    
    echo ""
    print_success "Development setup completed! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Activate virtual environment: source venv/bin/activate"
    echo "3. Run the application: uvicorn main:app --reload"
    echo "4. Visit http://localhost:8000/docs for API documentation"
    echo ""
    echo "Optional:"
    echo "- Use Docker: docker-compose up"
    echo "- Run tests: pytest"
    echo "- Format code: black app/ main.py"
    echo "- Sort imports: isort app/ main.py"
}

# Run main function
main "$@"