Param(
  [int]$Epochs = 20,
  [string]$OutDir = "models_docker",
  [switch]$GPU
)

<# run_in_docker.ps1
   Usage: .\run_in_docker.ps1 -Epochs 20 -OutDir models_docker
   If you have an NVIDIA GPU and Docker configured, add -GPU to use the GPU image.
#>

$HostDir = (Split-Path -Path $PSScriptRoot -Resolve)
$Mount = "${HostDir}:/workspace"

$Cmds = "python -m pip install --upgrade pip; pip install -r requirements.txt; python -m src.train --csv data/sample_traffic.csv --out $OutDir --epochs $Epochs --contamination 0.05"

if ($GPU) {
  Write-Output "Starting TensorFlow GPU Docker container..."
  docker run --gpus all --rm -it -v "$Mount" -w /workspace tensorflow/tensorflow:latest-gpu bash -lc "$Cmds"
} else {
  Write-Output "Starting TensorFlow CPU Docker container..."
  docker run --rm -it -v "$Mount" -w /workspace tensorflow/tensorflow:latest bash -lc "$Cmds"
}

Write-Output "Finished. Models and outputs are in: $HostDir\$OutDir"
