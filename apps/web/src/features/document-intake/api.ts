export const document_intakeEndpoint = "/api/document-intake";
export const withCursor = (endpoint: string, cursor?: string) => cursor ? `${endpoint}?cursor=${encodeURIComponent(cursor)}` : endpoint;
