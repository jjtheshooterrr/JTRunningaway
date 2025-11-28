"use client";

import { useState } from "react";

interface PromptFormProps {
  onJobCreated: (jobId: string) => void;
}

export default function PromptForm({ onJobCreated }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("Cinematic");
  const [duration, setDuration] = useState(4);
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [seed, setSeed] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          style: style === "None" ? null : style,
          duration_seconds: duration,
          aspect_ratio: aspectRatio,
          seed: seed ? parseInt(seed) : null,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to create job");
      }

      const data = await res.json();
      onJobCreated(data.job_id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 p-6 bg-gray-800 rounded-lg shadow-xl border border-gray-700">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Prompt</label>
        <textarea
          required
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full p-3 bg-gray-900 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          placeholder="Describe your video..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Style</label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full p-2 bg-gray-900 border border-gray-600 rounded-md text-white"
          >
            {["None", "Cinematic", "Anime", "3D render", "Pixel art"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Duration</label>
          <div className="flex space-x-2">
            {[2, 4, 6].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDuration(d)}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                  duration === d ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {d}s
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Aspect Ratio</label>
          <div className="flex space-x-2">
            {["1:1", "16:9", "9:16"].map((ar) => (
              <button
                key={ar}
                type="button"
                onClick={() => setAspectRatio(ar)}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                  aspectRatio === ar ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {ar}
              </button>
            ))}
          </div>
        </div>

        <div>
           <label className="block text-sm font-medium text-gray-300 mb-2">Seed (Optional)</label>
           <input
             type="number"
             value={seed}
             onChange={(e) => setSeed(e.target.value)}
             className="w-full p-2 bg-gray-900 border border-gray-600 rounded-md text-white"
             placeholder="Random"
           />
        </div>
      </div>

      {error && <div className="text-red-400 text-sm">{error}</div>}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-md hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
      >
        {loading ? "Creating Job..." : "Generate Video"}
      </button>
    </form>
  );
}
