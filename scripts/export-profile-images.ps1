param(
    [ValidateSet("png", "svg", "pdf")]
    [string]$Format = "png",

    [string]$Mmdc = "mmdc",

    [string]$PuppeteerConfigFile = "scripts\puppeteer-config.json",

    [int]$Width = 1400,

    [int]$Height = 1000,

    [switch]$SkipImageExport
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Harness = Join-Path $Root ".venv\Scripts\network-diagram-harness.exe"
$DefaultMmdc = Join-Path $env:APPDATA "npm\mmdc.cmd"

if (-not (Test-Path -LiteralPath $Mmdc) -and (Test-Path -LiteralPath $DefaultMmdc)) {
    $Mmdc = $DefaultMmdc
}

$Diagrams = @(
    @{
        Name = "home-network"
        Scope = "private"
        Source = "local\home-network.local.yml"
        Preview = "output\home-network.md"
        Mermaid = "output\home-network.mmd"
        Image = "output\images\private\home-network.$Format"
    },
    @{
        Name = "profile-home-lab"
        Scope = "public"
        Source = "examples\profile-home-lab.yml"
        Preview = "docs\examples\profile-home-lab.md"
        Mermaid = "output\profile-home-lab.mmd"
        Image = "output\images\public\profile-home-lab.$Format"
    }
)

if (-not (Test-Path -LiteralPath $Harness)) {
    throw "Harness executable not found: $Harness"
}

Push-Location $Root
try {
    foreach ($Diagram in $Diagrams) {
        if (-not (Test-Path -LiteralPath $Diagram.Source)) {
            Write-Host "Skipping $($Diagram.Scope): source not found: $($Diagram.Source)"
            continue
        }

        Write-Host "Validating $($Diagram.Scope): $($Diagram.Source)"
        & $Harness validate $Diagram.Source
        if ($LASTEXITCODE -ne 0) { throw "Command failed: validate $($Diagram.Source)" }

        Write-Host "Writing preview: $($Diagram.Preview)"
        & $Harness preview $Diagram.Source --output $Diagram.Preview
        if ($LASTEXITCODE -ne 0) { throw "Command failed: preview $($Diagram.Source)" }

        Write-Host "Writing Mermaid: $($Diagram.Mermaid)"
        & $Harness render $Diagram.Source --output $Diagram.Mermaid
        if ($LASTEXITCODE -ne 0) { throw "Command failed: render $($Diagram.Source)" }

        if (-not $SkipImageExport) {
            Write-Host "Writing image: $($Diagram.Image)"
            & $Harness export $Diagram.Source --output $Diagram.Image --mmdc $Mmdc --puppeteer-config-file $PuppeteerConfigFile --width $Width --height $Height
            if ($LASTEXITCODE -ne 0) { throw "Command failed: export $($Diagram.Source)" }
        }
    }
}
finally {
    Pop-Location
}
