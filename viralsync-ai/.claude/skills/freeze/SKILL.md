---
name: freeze
description: 파일 수정을 한 폴더 안으로 제한한다 (예: /freeze src/lib/services). 위험한 작업 중 다른 곳을 건드리지 않게 할 때 사용. 해제는 /unfreeze.
---
# /freeze <폴더>

1. 인자로 받은 폴더가 이 저장소 안에 있는지 확인 (없으면 캡틴에게 물어본다).
2. `.claude/freeze` 파일에 그 폴더의 **저장소 기준 상대 경로** 한 줄을 쓴다 (예: `src/lib/services`).
3. 이제 안전 훅(`.claude/hooks/guard.mjs`)이 그 밖의 Edit/Write 를 막는다.
4. 캡틴에게 “수정 범위: <폴더>. 풀려면 /unfreeze” 라고 알린다.
