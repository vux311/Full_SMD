import axios, { AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9999";

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

// Extend InternalAxiosRequestConfig to support skipSnake option
export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig<any> {
  skipSnake?: boolean;
}

const instance = axios.create({
  baseURL: API_BASE,
  headers: { Accept: "application/json" },
});

// Request interceptor: attach Authorization and convert body keys to snake_case
instance.interceptors.request.use((config: CustomAxiosRequestConfig) => {
  try {
    // Attach token if in browser
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) (config.headers as any)["Authorization"] = `Bearer ${token}`;
    }

    const method = (config.method || "get").toLowerCase();
    const shouldSnake = config.skipSnake === true ? false : (method === "post" || method === "put" || method === "patch");

    if (shouldSnake && config.data && isPlainObject(config.data)) {
      config.data = convertKeysToSnake(config.data);
    }
  } catch (e) {
    // ignore
    console.error("axios request interceptor error", e);
  }
  return config;
});

// Response interceptor: pass through (backend returns camelCase per contract)
instance.interceptors.response.use(
  (res) => res,
  (err) => {
    return Promise.reject(err);
  }
);

export default instance;