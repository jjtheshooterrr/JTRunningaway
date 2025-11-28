"use client";

import { useEffect, useState } from "react";

interface JobStatusProps {
    jobId: string;
}

interface JobDetail {
    job_id: string;
    status: string;
    video_url?: string;
    error_message?: string;
}

export default function JobStatus({ jobId }: JobStatusProps) {
    const [job, setJob] = useState<JobDetail | null>(null);

    useEffect(() => {
        let interval: NodeJS.Timeout;

        const fetchJob = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/job/${jobId}`);
                if (res.ok) {
                    const data = await res.json();
                    setJob(data);
                    if (data.status === "done" || data.status === "failed") {
                        clearInterval(interval);
                    }
                }
            } catch (error) {
                console.error("Error fetching job:", error);
            }
        };

        fetchJob();
        interval = setInterval(fetchJob, 2000);

        return () => clearInterval(interval);
    }, [jobId]);

    if (!job) return <div className="text-gray-400 animate-pulse">Loading job details...</div>;

    return (
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700 flex flex-col items-center justify-center min-h-[400px]">
            {job.status === "queued" && (
                <div className="text-center">
                    <div className="text-yellow-400 text-xl font-bold mb-2">Queued</div>
                    <p className="text-gray-400">Waiting for worker...</p>
                </div>
            )}

            {job.status === "running" && (
                <div className="text-center">
                    <div className="text-blue-400 text-xl font-bold mb-2 animate-pulse">Generating...</div>
                    <p className="text-gray-400">This may take a minute.</p>
                </div>
            )}

            {job.status === "failed" && (
                <div className="text-center text-red-500">
                    <div className="text-xl font-bold mb-2">Failed</div>
                    <p>{job.error_message}</p>
                </div>
            )}

            {job.status === "done" && job.video_url && (
                <div className="w-full">
                    <video
                        src={job.video_url}
                        controls
                        loop
                        autoPlay
                        className="w-full rounded-lg shadow-lg mb-4"
                    />
                    <a
                        href={job.video_url}
                        download
                        className="block w-full text-center py-2 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors"
                    >
                        Download Video
                    </a>
                </div>
            )}
        </div>
    );
}
