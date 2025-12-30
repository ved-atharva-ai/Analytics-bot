import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Bot, User, Loader2, Trash2, PlusCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { useLanguage } from '../context/LanguageContext';

const ChatInterface = ({ role }) => {
    const { t } = useLanguage();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: t('welcome_message') }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const fetchHistory = async () => {
        try {
            const res = await axios.get(`http://localhost:8000/history/${role}`);
            if (res.data.length > 0) {
                setMessages(res.data);
            } else {
                setMessages([
                    { role: 'assistant', content: t('welcome_message') }
                ]);
            }
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, [role]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await axios.post('http://localhost:8000/chat', {
                message: userMessage.content,
                role: role
            });

            const botMessage = {
                role: 'assistant',
                content: res.data.response,
                image: res.data.image_url
            };
            setMessages(prev => [...prev, botMessage]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: t('error_message') }]);
        } finally {
            setLoading(false);
        }
    };

    const handleNewChat = async () => {
        if (window.confirm(t('confirm_new_chat'))) {
            try {
                await axios.delete(`http://localhost:8000/history/${role}`);
                setMessages([
                    { role: 'assistant', content: t('welcome_message') }
                ]);
            } catch (err) {
                console.error("Failed to delete history", err);
            }
        }
    };

    return (
        <div className="max-w-4xl mx-auto h-full flex flex-col">
            {/* Header with New Chat button */}
            <div className="flex justify-between items-center mb-4 pb-4 border-b border-white/10">
                <h2 className="text-xl font-bold text-gray-300">
                    {t('chat_assistant')}
                </h2>
                <button
                    onClick={handleNewChat}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors"
                >
                    <PlusCircle size={18} />
                    {t('new_chat')}
                </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-6 pr-4 pb-4 custom-scrollbar">
                <AnimatePresence>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'assistant'
                                ? 'bg-gradient-to-br from-blue-500 to-purple-500'
                                : 'bg-gray-700'
                                }`}>
                                {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
                            </div>

                            <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className={`p-4 rounded-2xl ${msg.role === 'assistant'
                                    ? 'bg-white/10 border border-white/5 text-gray-100'
                                    : 'bg-blue-600 text-white'
                                    }`}>
                                    <div className="prose prose-invert max-w-none">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                img: ({ node, ...props }) => {
                                                    // Construct full URL for images
                                                    let src = props.src;
                                                    if (src.startsWith('/')) {
                                                        src = `http://localhost:8000${src}`;
                                                    }
                                                    console.log('Rendering image:', src);
                                                    return (
                                                        <img
                                                            {...props}
                                                            src={src}
                                                            className="rounded-lg border border-white/10 mt-2 max-w-full"
                                                            alt={props.alt || "Generated Chart"}
                                                            onError={(e) => {
                                                                console.error('Image failed to load:', src);
                                                                e.target.style.border = '2px solid red';
                                                            }}
                                                            onLoad={() => console.log('Image loaded successfully:', src)}
                                                        />
                                                    );
                                                }
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                                {msg.image && (
                                    <motion.img
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        src={`http://localhost:8000${msg.image}`}
                                        alt="Chart"
                                        className="rounded-xl border border-white/10 shadow-lg max-w-md"
                                    />
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-4"
                    >
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <Bot size={20} />
                        </div>
                        <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-center gap-3">
                            <Loader2 size={18} className="animate-spin text-blue-400" />
                            <span className="text-sm text-gray-400">{t('analyzing')}</span>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="mt-4">
                <form onSubmit={handleSend} className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={t('ask_placeholder')}
                        className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-6 pr-14 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 top-2 p-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
                    >
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
