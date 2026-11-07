import {Config} from '@remotion/cli/config';
// 컨테이너에 미리 깔린 Chromium 사용 (remotion이 브라우저를 따로 내려받지 않게)
Config.setBrowserExecutable(process.env.REMOTION_CHROME ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell');
Config.setVideoImageFormat('jpeg');
Config.setConcurrency(2);
