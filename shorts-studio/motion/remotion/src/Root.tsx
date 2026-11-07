import React from 'react';
import {Composition} from 'remotion';
import {CountUp, countUpSchema} from './CountUp';

// 쇼츠 규격 1080x1920 · 30fps. props는 --props='{"label":...}' 로 장면마다 바꾼다.
export const Root: React.FC = () => (
  <>
    <Composition
      id="CountUp"
      component={CountUp}
      durationInFrames={150}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={countUpSchema}
    />
  </>
);
