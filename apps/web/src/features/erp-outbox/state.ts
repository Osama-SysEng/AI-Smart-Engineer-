export type FeatureState<T> = { status: "idle" | "loading" | "ready" | "error"; data: T[]; error: string | null };
export const initialState = <T>(): FeatureState<T> => ({ status: "idle", data: [], error: null });
