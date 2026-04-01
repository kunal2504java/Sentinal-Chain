export type EventRecord = {
  id: number;
  event_type: string;
  camera_id: string;
  timestamp: string;
  clip_path: string;
  clip_hash: string;
  ipfs_cid: string;
  tx_hash: string;
  confidence: number;
  created_at: string;
};

export type EventStats = {
  total_events: number;
  events_today: number;
  integrity_rate: number;
};

export type VerifyResult = {
  match: boolean;
  on_chain_hash: string | null;
  local_hash: string;
};
