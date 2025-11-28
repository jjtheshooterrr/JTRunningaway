"use client";

import { useState } from "react";
import PromptForm from "./components/PromptForm";
import JobStatus from "./components/JobStatus";
import HistoryList from "./components/HistoryList";

export default function Home() {
    const [activeJobId, setActiveJobId] = useState<string | null>(null);
    const [refreshHistory, setRefreshHistory] = useState(0);

    const handleJobCreated = (jobId: string) => {
        setActiveJobId(jobId);
        // Trigger history refresh after a short delay to allow DB to update
        setTimeout(() => setRefreshHistory(prev => prev + 1), 500);
    };

    return (
        <main className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        Local Video Generator
                    </h1>
                    <p className="text-gray-400 mt-2">Generate AI videos locally with SDXL + SVD</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left Column: Form */}
                    <div className="lg:col-span-4">
                        <PromptForm onJobCreated={handleJobCreated} />
                    </div>

                    {/* Middle Column: Preview */}
                    <div className="lg:col-span-5">
                        {activeJobId ? (
                            <JobStatus jobId={activeJobId} />
                        ) : (
                            <div className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700 flex items-center justify-center min-h-[400px] text-gray-500">
                                Select a job or create a new one to preview
                            </div>
                        )}
                    </div>

                    {/* Right Column: History */}
                    <div className="lg:col-span-3">
                        <HistoryList onSelectJob={setActiveJobId} refreshTrigger={refreshHistory} />
                    </div>
                </div>
            </div>
        </main>
    );
}
