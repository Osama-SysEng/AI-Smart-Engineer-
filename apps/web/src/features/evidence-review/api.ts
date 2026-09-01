export const evidence_reviewEndpoint = "/api/evidence-review";
export const withCursor = (endpoint: string, cursor?: string) => cursor ? `${endpoint}?cursor=${encodeURIComponent(cursor)}` : endpoint;
