import axios, { AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";

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

function toCamelCase(str: string) {
  return str.replace(/([-_][a-z])/ig, ($1) => {
    return $1.toUpperCase()
      .replace('-', '')
      .replace('_', '');
  });
}

function convertKeysToCamel(obj: any): any {
  if (Array.isArray(obj)) return obj.map(convertKeysToCamel);
  if (!isPlainObject(obj)) return obj;
  const out: any = {};
  for (const key of Object.keys(obj)) {
    const camelKey = toCamelCase(key);
    out[camelKey] = convertKeysToCamel((obj as any)[key]);
  }
  return out;
}

// Extend InternalAxiosRequestConfig to support skipSnake and skipCamel option
export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig<any> {
  skipSnake?: boolean;
  skipCamel?: boolean;
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
      if (token && config.headers) {
        // Use standard header setting
        config.headers.Authorization = `Bearer ${token}`;
        console.debug("Requesting with token:", config.url);
      }
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

// Response interceptor: handle errors and convert body keys to camelCase
instance.interceptors.response.use(
  (res) => {
    const config = res.config as CustomAxiosRequestConfig;
    if (config.skipCamel !== true && res.data && (isPlainObject(res.data) || Array.isArray(res.data))) {
      res.data = convertKeysToCamel(res.data);
    }
    return res;
  },
  (err) => {
    // Handle 401 Unauthorized - token expired
    if (err.response?.status === 401) {
      console.error("⚠️ Bị lỗi 401 ở đây nè:", err.config?.url);
      if (typeof window !== "undefined") {
        const currentPath = window.location.pathname;
        // Don't redirect if already on login page
        if (currentPath !== "/login") {
          // localStorage.removeItem("access_token");
          // localStorage.removeItem("refresh_token");
          // localStorage.removeItem("role");
          // window.location.href = "/login";
        }
      }
    }
    
    // Handle 403 Forbidden - no permission
    if (err.response?.status === 403) {
      const message = err.response?.data?.message || "Bạn không có quyền thực hiện hành động này";
      console.warn("403 Forbidden:", message);
      
      // Add user-friendly message to error for components to use
      err.userMessage = message;
    }
    
    return Promise.reject(err);
  }
);

export default instance;