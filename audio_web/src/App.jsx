import React, { useState, useEffect } from 'react';

function App() {
    const [activeTab, setActiveTab] = useState('submit');
    const [submissions, setSubmissions] = useState([]);

    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [file, setFile] = useState(null);

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ text: '', type: '' });

    const fetchSubmissions = async () => {
        try {
            const res = await fetch('/api/submissions');
            if (res.ok) {
                const data = await res.json();
                setSubmissions(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (activeTab === 'dashboard') {
            fetchSubmissions();
        }
    }, [activeTab]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name || !phone || !file) {
            setMessage({ text: 'Please fill all fields and select a file', type: 'error' });
            return;
        }

        setLoading(true);
        setMessage({ text: '', type: '' });

        const formData = new FormData();
        formData.append('name', name);
        formData.append('phone', phone);
        formData.append('audio', file);

        try {
            const res = await fetch('/api/submissions', {
                method: 'POST',
                body: formData,
            });

            const data = await res.json();

            if (!res.ok) {
                setMessage({ text: data.detail || 'Submission failed', type: 'error' });
            } else {
                setMessage({ text: 'Audio submitted securely and processed!', type: 'success' });
                setName('');
                setPhone('');
                setFile(null);
                e.target.reset();
            }
        } catch (err) {
            setMessage({ text: 'Network connection failed', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen relative p-6 bg-gray-950 font-sans text-gray-100 selection:bg-indigo-500/30">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-gray-950 to-gray-950 -z-10"></div>

            <div className="max-w-4xl mx-auto">
                <header className="mb-10 text-center">
                    <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 mb-2">
                        ConsultBae Audio Sync
                    </h1>
                    <p className="text-gray-400">Task 3: Automated Audio Signal Parsing Database</p>
                </header>

                <div className="flex justify-center space-x-4 mb-8">
                    <button
                        onClick={() => setActiveTab('submit')}
                        className={`px-6 py-2.5 rounded-full font-medium transition-all duration-300 ${activeTab === 'submit' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25' : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'}`}
                    >
                        Submit Audio
                    </button>
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`px-6 py-2.5 rounded-full font-medium transition-all duration-300 ${activeTab === 'dashboard' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25' : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'}`}
                    >
                        Dashboard
                    </button>
                </div>

                {activeTab === 'submit' && (
                    <div className="glass rounded-2xl p-8 shadow-2xl max-w-lg mx-auto">
                        {message.text && (
                            <div className={`mb-6 p-4 rounded-lg flex items-center border ${message.type === 'error' ? 'bg-red-500/10 border-red-500/50 text-red-400' : 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400'}`}>
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                                    placeholder="e.g. Rahul Chopra"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Registered Phone Number</label>
                                <input
                                    type="tel"
                                    value={phone}
                                    onChange={e => setPhone(e.target.value)}
                                    className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                                    placeholder="10-digit database phone"
                                />
                                <p className="text-xs text-gray-500 mt-2">Must strictly match a worker stored in the Core SQL database.</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Audio Upload</label>
                                <div className="relative border-2 border-dashed border-gray-700 rounded-xl bg-gray-900/50 p-6 flex flex-col items-center justify-center hover:border-indigo-500/50 transition-colors cursor-pointer group">
                                    <svg className="w-10 h-10 text-gray-500 group-hover:text-indigo-400 mb-3 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                    </svg>
                                    <span className="text-gray-400 font-medium">{file ? file.name : "Select an audio file..."}</span>
                                    <input
                                        type="file"
                                        accept="audio/*"
                                        onChange={e => setFile(e.target.files[0])}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-all font-semibold rounded-xl py-3.5 shadow-lg flex items-center justify-center"
                            >
                                {loading ? (
                                    <span className="animate-pulse">Processing...</span>
                                ) : (
                                    "Initiate Signal Pipeline"
                                )}
                            </button>
                        </form>
                    </div>
                )}

                {activeTab === 'dashboard' && (
                    <div className="space-y-4">
                        {submissions.length === 0 ? (
                            <div className="glass rounded-2xl p-12 text-center text-gray-400">
                                No submittions recorded yet.
                            </div>
                        ) : (
                            submissions.map(sub => (
                                <div key={sub.submission_id} className="glass rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-center gap-6">

                                    <div className="flex-1 min-w-0 w-full">
                                        <div className="flex items-center gap-3 mb-1">
                                            <h3 className="font-semibold text-lg text-gray-100 truncate">{sub.canonical_name}</h3>
                                            <span className="text-xs bg-gray-800 text-gray-400 px-2.5 py-1 rounded-full border border-gray-700 font-mono tracking-wider">
                                                {sub.phone_10}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-500 mb-4 items-center flex gap-1">
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            {new Date(sub.submitted_at).toLocaleString()}
                                        </p>

                                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                                            <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                                                <div className="text-xs font-medium text-gray-500 mb-1">Duration</div>
                                                <div className="font-mono text-cyan-400">{sub.duration_seconds?.toFixed(2)}s</div>
                                            </div>
                                            <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                                                <div className="text-xs font-medium text-gray-500 mb-1">Sample Rate</div>
                                                <div className="font-mono text-indigo-400">{sub.sample_rate_hz} Hz</div>
                                            </div>
                                            <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                                                <div className="text-xs font-medium text-gray-500 mb-1">Bitrate</div>
                                                <div className="font-mono text-emerald-400">{sub.bitrate_kbps} kbps</div>
                                            </div>
                                            <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                                                <div className="text-xs font-medium text-gray-500 mb-1">Loudness</div>
                                                <div className="font-mono text-blue-400">{sub.loudness_db?.toFixed(1)} dB</div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="w-full md:w-auto bg-gray-900 p-2 rounded-xl border border-gray-800">
                                        <audio
                                            controls
                                            src={sub.file_path}
                                            className="w-full md:w-64 h-12 outline-none"
                                        />
                                    </div>

                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
