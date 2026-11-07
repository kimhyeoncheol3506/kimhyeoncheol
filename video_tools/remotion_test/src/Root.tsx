import React from "react";
import { Composition } from "remotion";
import { Hello } from "./Hello";
export const Root: React.FC = () => (
  <Composition id="Hello" component={Hello} durationInFrames={150} fps={30} width={1920} height={1080} />
);
