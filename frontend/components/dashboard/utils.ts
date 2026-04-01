export function formatTimestamp(value: string) {
  const date = new Date(value);
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function shortHash(value: string | null | undefined, head = 10, tail = 8) {
  if (!value) {
    return "Unavailable";
  }
  if (value.length <= head + tail + 3) {
    return value;
  }
  return `${value.slice(0, head)}...${value.slice(-tail)}`;
}
