import {Config} from '@remotion/cli/config';
// 클라우드 세션: 미리 설치된 Playwright 헤드리스 셸을 쓴다. PC에서는 이 줄을 지우면 Remotion이 직접 내려받는다.
if (process.env.REMOTION_BROWSER) Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
Config.setVideoImageFormat('jpeg');
