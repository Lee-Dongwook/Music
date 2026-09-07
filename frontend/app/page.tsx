// app/page.tsx
"use client";

import { useState, useEffect } from "react";
import {
  requestGenerateMusic,
  fetchTaskStatus,
  fetchMusicHistory,
} from "@/lib/api";
import { MusicTask } from "@/types/music";
import AudioPlayer from "@/components/AudioPlayer";
import { Sparkles, Loader2, Music, RefreshCw } from "lucide-react";

export default function HomePage() {
  const [prompt, setPrompt] = useState("");
  const [lyrics, setLyrics] = useState("");
  const [title, setTitle] = useState("");
  const [tasks, setTasks] = useState<MusicTask[]>([]);
  const [activeTask, setActiveTask] = useState<MusicTask | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await fetchMusicHistory();
        setTasks(history);
        if (history.length > 0 && !activeTask) {
          const completedTrack = history.find((t) => t.status === "completed");
          if (completedTrack) setActiveTask(completedTrack);
        }
      } catch (e) {
        console.error(e);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    const pendingTasks = tasks.filter(
      (t) => t.status === "pending" || t.status === "processing",
    );
    if (pendingTasks.length === 0) return;

    const interval = setInterval(async () => {
      const updatedHistory = await fetchMusicHistory();
      setTasks(updatedHistory);

      // 현재 재생 중이거나 선택된 트랙이 완공되었을 때 갱신
      if (activeTask) {
        const currentUpdated = updatedHistory.find(
          (t) => t.task_id === activeTask.task_id,
        );
        if (currentUpdated) setActiveTask(currentUpdated);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [tasks, activeTask]);

  const loadHistory = async () => {
    try {
      const history = await fetchMusicHistory();
      setTasks(history);
      if (history.length > 0 && !activeTask) {
        const completedTrack = history.find((t) => t.status === "completed");
        if (completedTrack) setActiveTask(completedTrack);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // 생성 요청 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsSubmitting(true);
    try {
      const newTask = await requestGenerateMusic({ prompt, lyrics, title });
      setTasks((prev) => [newTask, ...prev]);
      setActiveTask(newTask);
      setPrompt("");
      setLyrics("");
      setTitle("");
    } catch (error) {
      alert("음악 생성 중 오류가 발생했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-neutral-200 font-sans">
      {/* 좌측: 프롬프트 입력 폼 */}
      <div className="w-1/3 border-r border-neutral-800 p-6 flex flex-col justify-between overflow-y-auto">
        <div>
          <div className="flex items-center gap-2 mb-8">
            <div className="p-2 bg-violet-600/20 rounded-lg text-violet-400">
              <Sparkles className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-wide">
              Music AI Studio
            </h1>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-2">
                곡 제목 (Title)
              </label>
              <input
                type="text"
                placeholder="예: Midnight City Walk"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-violet-500 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-2">
                음악 스타일 프롬프트 (Prompt)
              </label>
              <textarea
                rows={3}
                placeholder="예: Upbeat synthwave with energetic drum beats and retro bass"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
                className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-4 text-sm text-white focus:outline-none focus:border-violet-500 transition resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-2">
                가사 (Lyrics - 선택 사항)
              </label>
              <textarea
                rows={5}
                placeholder="[Verse]&#10;고요한 밤거리 속에&#10;&#10;[Chorus]&#10;빛나는 조명 아래 서있어"
                value={lyrics}
                onChange={(e) => setLyrics(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-4 text-sm text-white focus:outline-none focus:border-violet-500 transition resize-none font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !prompt}
              className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-neutral-800 text-white font-semibold py-3.5 rounded-lg flex items-center justify-center gap-2 transition shadow-lg shadow-violet-600/20"
            >
              {isSubmitting ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
              음악 생성하기
            </button>
          </form>
        </div>
      </div>

      {/* 우측: 태스크 목록 및 오디오 플레이어 */}
      <div className="flex-1 flex flex-col justify-between p-6 bg-neutral-950 overflow-hidden">
        {/* 상단: 히스토리 트랙 목록 */}
        <div className="flex-1 overflow-y-auto pr-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Music className="w-5 h-5 text-violet-400" />
              생성 내역 (Track Library)
            </h2>
            <button
              onClick={loadHistory}
              className="p-2 text-neutral-400 hover:text-white transition"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {tasks.map((task) => (
              <div
                key={task.task_id}
                onClick={() =>
                  task.status === "completed" && setActiveTask(task)
                }
                className={`p-4 rounded-xl border transition flex items-center justify-between cursor-pointer ${
                  activeTask?.task_id === task.task_id
                    ? "bg-neutral-900 border-violet-500/50"
                    : "bg-neutral-900/50 border-neutral-800/80 hover:border-neutral-700"
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-neutral-800 rounded-lg flex items-center justify-center overflow-hidden">
                    {task.cover_image_url ? (
                      <img
                        src={task.cover_image_url}
                        alt="cover"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Music className="w-6 h-6 text-neutral-500" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      {task.title}
                    </h3>
                    <p className="text-xs text-neutral-400 truncate max-w-md">
                      {task.prompt}
                    </p>
                  </div>
                </div>

                {/* 상태 배지 */}
                <div>
                  {task.status === "pending" && (
                    <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2.5 py-1 rounded-full">
                      대기 중
                    </span>
                  )}
                  {task.status === "processing" && (
                    <span className="text-xs bg-violet-500/10 text-violet-400 border border-violet-500/20 px-2.5 py-1 rounded-full flex items-center gap-1.5">
                      <Loader2 className="w-3 h-3 animate-spin" /> 생성 중...
                    </span>
                  )}
                  {task.status === "completed" && (
                    <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                      완료
                    </span>
                  )}
                  {task.status === "failed" && (
                    <span className="text-xs bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2.5 py-1 rounded-full">
                      실패
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 하단 고정 오디오 플레이어 */}
        {activeTask && activeTask.audio_url && (
          <div className="pt-4 border-t border-neutral-800">
            <AudioPlayer
              audioUrl={activeTask.audio_url}
              title={activeTask.title}
            />
          </div>
        )}
      </div>
    </div>
  );
}
