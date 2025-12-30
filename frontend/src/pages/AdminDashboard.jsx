import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, Users, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

import { useLanguage } from '../context/LanguageContext';

const AdminDashboard = () => {
    const { t } = useLanguage();
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null);
    const [users, setUsers] = useState([]);

    useEffect(() => {
        // Fetch users (mock)
        axios.get('http://localhost:8000/users')
            .then(res => setUsers(res.data))
            .catch(err => console.error(err));
    }, []);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setStatus(null);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post('http://localhost:8000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setStatus({ type: 'success', message: res.data.info });
            setFile(null);
            // Trigger refresh of data preview
            window.dispatchEvent(new Event('fileUploaded'));
        } catch (err) {
            setStatus({ type: 'error', message: t('error_message') });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-8"
            >
                {/* Upload Section */}
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400">
                            <Upload size={24} />
                        </div>
                        <h2 className="text-2xl font-bold">{t('data_upload')}</h2>
                    </div>

                    <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-blue-500/50 transition-colors">
                        <input
                            type="file"
                            accept=".csv,.xlsx,.xls,.pdf"
                            onChange={handleFileChange}
                            className="hidden"
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-4">
                            <FileText size={48} className="text-gray-500" />
                            <div className="text-gray-400">
                                <span className="text-blue-400 font-medium">{t('click_to_upload')}</span> {t('drag_and_drop')}
                                <p className="text-sm mt-1">{t('supported_files')}</p>
                            </div>
                        </label>
                    </div>

                    {file && (
                        <div className="mt-4 p-4 bg-white/5 rounded-xl flex items-center justify-between">
                            <span className="text-sm text-gray-300">{file.name}</span>
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                            >
                                {uploading ? t('uploading') : t('upload_data')}
                            </button>
                        </div>
                    )}

                    {status && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className={`mt-4 p-4 rounded-xl flex items-center gap-3 ${status.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                }`}
                        >
                            {status.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                            <span className="text-sm">{status.message}</span>
                        </motion.div>
                    )}
                </div>

                {/* Users Section */}
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 bg-purple-500/20 rounded-xl text-purple-400">
                            <Users size={24} />
                        </div>
                        <h2 className="text-2xl font-bold">{t('active_users')}</h2>
                    </div>

                    <div className="space-y-4">
                        {users.map((user) => (
                            <div key={user.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-600 flex items-center justify-center font-bold text-sm">
                                        {user.username[0].toUpperCase()}
                                    </div>
                                    <div>
                                        <p className="font-medium">{user.username}</p>
                                        <p className="text-xs text-gray-400 capitalize">{user.role}</p>
                                    </div>
                                </div>
                                <div className={`w-2 h-2 rounded-full ${user.role === 'admin' ? 'bg-purple-500' : 'bg-green-500'}`}></div>
                            </div>
                        ))}
                    </div>
                </div>
            </motion.div>

            {/* Data Preview Section */}
            <DataPreview />
        </div>
    );
};

const DataPreview = () => {
    const { t } = useLanguage();
    const [data, setData] = useState(null);
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);

    const fetchFiles = async () => {
        try {
            const filesRes = await axios.get('http://localhost:8000/files');
            setFiles(filesRes.data);
            if (filesRes.data.length > 0 && !selectedFile) {
                setSelectedFile(filesRes.data[0]);
            }
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchFiles();
        window.addEventListener('fileUploaded', fetchFiles);
        return () => window.removeEventListener('fileUploaded', fetchFiles);
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            if (!selectedFile) return;
            try {
                const dataRes = await axios.get(`http://localhost:8000/data/preview?filename=${selectedFile}`);
                if (dataRes.data.columns) {
                    setData(dataRes.data);
                }
            } catch (err) {
                console.error(err);
            }
        };
        fetchData();
    }, [selectedFile]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
        >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-1 border-r border-white/10 pr-8">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <FileText size={20} className="text-blue-400" />
                        {t('uploaded_files')}
                    </h3>
                    <div className="space-y-2">
                        {files.length > 0 ? files.map((f, i) => (
                            <div
                                key={i}
                                onClick={() => setSelectedFile(f)}
                                className={`p-3 rounded-lg text-sm truncate cursor-pointer transition-colors ${selectedFile === f
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white/5 text-gray-300 hover:bg-white/10'
                                    }`}
                            >
                                {f}
                            </div>
                        )) : <p className="text-gray-500 text-sm">{t('no_files')}</p>}
                    </div>
                </div>

                <div className="md:col-span-2">
                    <h3 className="text-xl font-bold mb-4">
                        {t('preview')}: <span className="text-blue-400">{selectedFile || 'None'}</span>
                    </h3>
                    {data && data.filename === selectedFile ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-300">
                                <thead className="text-xs text-gray-400 uppercase bg-white/5">
                                    <tr>
                                        {data.columns.map((col) => (
                                            <th key={col} className="px-6 py-3">{col}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.data.map((row, i) => (
                                        <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                                            {data.columns.map((col) => (
                                                <td key={col} className="px-6 py-4">{row[col]}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <p className="mt-4 text-xs text-gray-500">{t('showing_rows').replace('{total}', data.total_rows)}</p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                            <p>{t('select_file')}</p>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default AdminDashboard;
