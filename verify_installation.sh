#!/bin/bash
echo "======================================"
echo "Abhikarta - Installation Verification"
echo "======================================"
echo ""

echo "Checking directory structure..."
for dir in core agents tools workflows web config mcp_server data logs; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ directory exists"
    else
        echo "✗ $dir/ directory missing"
    fi
done

echo ""
echo "Checking core files..."
for file in run_server.py README.md QUICKSTART.md requirements.txt application.properties; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "Checking Python modules..."
python3 -c "import sys; sys.path.insert(0, '.'); from core.properties_configurator import PropertiesConfigurator; print('✓ Core modules load successfully')" 2>/dev/null || echo "✗ Error loading core modules"

echo ""
echo "Checking configuration files..."
for config in config/users/users.json config/agents/echo_agent.json config/dags/01_simple_sequential.json; do
    if [ -f "$config" ]; then
        echo "✓ $config exists"
    else
        echo "✗ $config missing"
    fi
done

echo ""
echo "======================================"
echo "Verification complete!"
echo "======================================"
