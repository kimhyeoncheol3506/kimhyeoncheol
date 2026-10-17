import { vi } from "vitest";
// "server-only" 는 Next 번들러 밖에서는 import 시 오류를 내므로 테스트에서 무력화합니다.
vi.mock("server-only", () => ({}));
