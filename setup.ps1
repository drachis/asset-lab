py -3.7 -m venv 
.\.venv\Scripts\activate.bat

$env:HYTHON="C:\Program Files\Side Effects Software\Houdini 19.0.720\bin\hython3.7.exe"
$env:TBB_MALLOC_DISABLE_REPLACEMENT = "1"
$env:HYTHON

pip install --upgrade pip
Get-Location | Set-Clipboard

git clone https://github.com/AcademySoftwareFoundation/OpenCue.git
cd OpenCue
git checkout v1.13.8
docker-compose up -d

Set-Location (Get-Clipboard)
pip install -r requirements.txt