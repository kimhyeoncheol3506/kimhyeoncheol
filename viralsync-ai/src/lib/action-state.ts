export interface ActionState {
  ok?: boolean;
  message?: string;
  errors?: Record<string, string>;
  /** 성공 시 표시용 부가 데이터 */
  data?: Record<string, unknown>;
}

export const initialState: ActionState = {};
