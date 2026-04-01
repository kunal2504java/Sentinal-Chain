export const AUTH_STORAGE_KEY = "sentinelchain-auth";

export function isValidPhoneOrEmail(value: string) {
  const trimmed = value.trim();
  const phonePattern = /^\d{10}$/;
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return phonePattern.test(trimmed) || emailPattern.test(trimmed);
}

export function isValidOtp(value: string) {
  return value.trim() === "123456";
}

export function createSession(identifier: string) {
  return JSON.stringify({
    identifier,
    authenticatedAt: new Date().toISOString(),
  });
}
