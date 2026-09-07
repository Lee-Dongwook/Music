export type TaskStatus = "pending" | "processing" | "completed" | "failed";

export interface MusicTask {
  task_id: string;
  status: TaskStatus;
  title: string;
  prompt: string;
  lyrics?: string;
  audio_url?: string;
  cover_image_url?: string;
  created_at: string;
  error_message?: string;
}

export interface GenerateRequest {
  prompt: string;
  lyrics?: string;
  title?: string;
}
