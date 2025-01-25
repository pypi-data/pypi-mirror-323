# PowerShell script to deploy package to PyPI

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("major", "minor", "patch")]
    [string]$VersionBump = "patch"
)

# Function to bump version
function Bump-Version {
    param (
        [string]$Version,
        [string]$Type
    )
    
    $parts = $Version.Split('.')
    switch ($Type) {
        "major" { 
            $parts[0] = [int]$parts[0] + 1
            $parts[1] = "0"
            $parts[2] = "0"
        }
        "minor" { 
            $parts[1] = [int]$parts[1] + 1
            $parts[2] = "0"
        }
        "patch" { 
            $parts[2] = [int]$parts[2] + 1
        }
    }
    return $parts -join "."
}

# Read current version from pyproject.toml
$content = Get-Content "pyproject.toml" -Raw
if ($content -match 'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"') {
    $currentVersion = $matches[1]
    $newVersion = Bump-Version -Version $currentVersion -Type $VersionBump
    Write-Host "Bumping version from $currentVersion to $newVersion"
    
    # Update version in pyproject.toml
    $content = $content -replace 'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"', "version = `"$newVersion`""
    Set-Content "pyproject.toml" -Value $content
} else {
    Write-Error "Could not find version in pyproject.toml"
    exit 1
}

# Clean up old builds
Write-Host "Cleaning up old builds..."
Remove-Item -Recurse -Force dist/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force *.egg-info/ -ErrorAction SilentlyContinue

# Build package
Write-Host "Building package..."
python -m build

# Upload to PyPI
Write-Host "Uploading to PyPI..."
python -m twine upload dist/*

Write-Host "Deployment complete!" 