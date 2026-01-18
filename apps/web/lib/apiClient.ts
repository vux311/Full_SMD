export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

function isPlainObject(value: any) {
  return Object.prototype.toString.call(value) === "[object Object]";
}

function toSnakeCase(str: string) {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

function convertKeysToSnake(obj: any): any {
  if (Array.isArray(obj)) return obj.map(convertKeysToSnake);
  if (!isPlainObject(obj)) return obj;
  const out: any = {};
  for (const key of Object.keys(obj)) {
    const snakeKey = toSnakeCase(key);
    out[snakeKey] = convertKeysToSnake((obj as any)[key]);
  }
  return out;
}

export async function apiFetch(path: string, opts: {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
  snake?: boolean; // convert body keys to snake_case when true (default for POST/PUT/PATCH)
} = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const token = (typeof window !== "undefined") ? localStorage.getItem("access_token") : null;

  const method = (opts.method || "GET").toUpperCase();
  const headers: Record<string, string> = {
    "Accept": "application/json",
    ...(opts.headers || {}),
  };

  if (token) headers["Authorization"] = `Bearer ${token}`;

  let body: any = undefined;
  if (opts.body !== undefined) {
    // If body is already a string, assume caller serialized it intentionally
    if (typeof opts.body === "string") {
      body = opts.body;
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    } else {
      const shouldSnake = opts.snake !== undefined ? opts.snake : (method === "POST" || method === "PUT" || method === "PATCH");
      const payload = shouldSnake ? convertKeysToSnake(opts.body) : opts.body;
      body = JSON.stringify(payload);
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }
  }

  const res = await fetch(url, { method, headers, body });
  // If possible, parse JSON, else throw
  const text = await res.text();
  let json: any = null;
  try { json = text ? JSON.parse(text) : null; } catch (e) { /* not json */ }

  if (!res.ok) {
    const err: any = new Error(json?.detail || `Request failed: ${res.status}`);
    (err as any).status = res.status;
    (err as any).data = json;
    throw err;
  }

  return json;
}
