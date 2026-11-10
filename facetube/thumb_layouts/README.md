# 썸네일 새 모양(플러그인)

`<이름>.py` 에 `def page(t, fonts_uri, W, H) -> str`(완성 HTML)를 두면 대본 `thumbnail.layout: <이름>` 으로 쓴다.
글꼴: `@font-face{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}`.
채널 안에서 모양·바탕색이 겹치지 않게(내규칙 2026-11-07). 이미 쓴 모양: default·tiles·versus·badge·phone·calendar·film.
