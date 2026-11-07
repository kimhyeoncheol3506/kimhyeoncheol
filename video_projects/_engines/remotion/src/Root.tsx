import React from 'react';
import {Composition} from 'remotion';
import {CounterBars} from './CounterBars';

export const RemotionRoot: React.FC = () => (
  <Composition id="CounterBars" component={CounterBars} durationInFrames={150} fps={30} width={1920} height={1080}
    defaultProps={{title: '1720년 남해회사 주가', from: 128, to: 1050, unit: '파운드',
      bars: [{label: '1월', value: 128}, {label: '3월', value: 330}, {label: '5월', value: 500}, {label: '6월 말', value: 1050}]}} />
);
