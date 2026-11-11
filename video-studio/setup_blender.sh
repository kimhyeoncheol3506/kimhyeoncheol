#!/usr/bin/env bash
# Blender 4.5 LTS(헤드리스) 설치 → /home/user/ext/blender-4.5.9-linux-x64/blender (저장소 밖, 약 1GB)
# workbench 엔진용 소프트웨어 GL(libEGL·mesa)도 함께. cycles 는 CPU 로 렌더.
set -e
E=/home/user/ext; mkdir -p $E; cd $E
[ -x blender-4.5.9-linux-x64/blender ] || { curl -sSL -o blender.tar.xz https://download.blender.org/release/Blender4.5/blender-4.5.9-linux-x64.tar.xz && tar xJf blender.tar.xz && rm -f blender.tar.xz; }
apt-get install -y -q libegl1 libegl-mesa0 libgl1-mesa-dri libgl1 >/dev/null 2>&1 || { apt-get update -q >/dev/null && apt-get install -y -q libegl1 libegl-mesa0 libgl1-mesa-dri libgl1 >/dev/null; }
$E/blender-4.5.9-linux-x64/blender -b --version | head -1
