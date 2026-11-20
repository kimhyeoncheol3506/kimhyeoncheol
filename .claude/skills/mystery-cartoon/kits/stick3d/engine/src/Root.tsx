import React from "react";
import { Composition } from "remotion";
import "@fontsource/inter/900.css";
import { Main } from "./Main";
import { NvidiaV4 } from "./videos/NvidiaV4";
import { Voynich } from "./videos/Voynich";
// DURATION: set durationInFrames = ceil(voiceover_seconds * 30). Use --props or edit per video.
export const Root: React.FC = () => <>
  <Composition id="Main" component={Main} width={720} height={1280} fps={30} durationInFrames={60} />
  <Composition id="NvidiaV4" component={NvidiaV4} width={720} height={1280} fps={30} durationInFrames={661} />
  <Composition id="Voynich" component={Voynich} width={720} height={1280} fps={30} durationInFrames={454} />
</>;
