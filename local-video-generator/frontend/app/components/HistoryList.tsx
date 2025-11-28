"use client";

import { useEffect, useState } from "react";

interface HistoryListProps {
    onSelectJob: (jobId: string) => void;
    refreshTrigger: number;
}

interface JobSummary {
    job_id: string;
    prompt: string;
    status: string;
    thumbnail_url?: string;
    created_at: string;
}

export default function HistoryList({ onSelectJob, refreshTrigger }: HistoryListProps) {
    const [jobs, setJobs] = useState<JobSummary[]>([]);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/jobs/recent`);
                if (res.ok) {
                    const data = await res.json();
                    setJobs(data.jobs);
                }
            } catch (error) {
                console.error("Error fetching history:", error);
            }
        };

        fetchHistory();
    }, [refreshTrigger]);

    return (
        <div className="bg-gray-800 rounded-lg p-4 shadow-xl border border-gray-700 h-full overflow-y-auto max-h-[600px]">
            <h2 className="text-xl font-bold text-white mb-4">Recent Jobs</h2>
            <div className="space-y-3">
                {jobs.map((job) => (
                    <div
                        key={job.job_id}
                        onClick={() => onSelectJob(job.job_id)}
                        className="flex items-center space-x-3 p-2 hover:bg-gray-700 rounded cursor-pointer transition-colors"
                    >
                        <div className="w-16 h-16 bg-gray-900 rounded overflow-hidden flex-shrink-0">
                            {job.thumbnail_url ? (
                                <img src={job.thumbnail_url} alt="thumb" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-gray-600 text-xs">No Img</div>
                            )}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{job.prompt}</p>
                            <div className="flex items-center justify-between mt-1">
                                <span className={`text-xs px-2 py-0.5 rounded-full ${job.status === 'done' ? 'bg-green-900 text-green-300' :
                                        job.status === 'failed' ? 'bg-red-900 text-red-300' :
                                            'bg-blue-900 text-blue-300'
                                    }`}>
                                    {job.status}
                                </span>
                                <span className="text-xs text-gray-500">
                                    {new Date(job.created_at).toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
