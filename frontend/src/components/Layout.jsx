import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Upload, User, Settings, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';

const Layout = ({ children, role, setRole }) => {
    const location = useLocation();

    const navItems = [
        { path: '/chat', icon: MessageSquare, label: 'Chat' },
        ...(role === 'admin' ? [{ path: '/admin', icon: Upload, label: 'Admin Dashboard' }] : []),
    ];

    return (
        <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white overflow-hidden">
            {/* Sidebar */}
            <motion.div
                initial={{ x: -100 }}
                animate={{ x: 0 }}
                className="w-64 bg-white/5 backdrop-blur-lg border-r border-white/10 p-6 flex flex-col"
            >
                <div className="flex items-center gap-3 mb-10">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                        <span className="font-bold text-xl">A</span>
                    </div>
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                        AnalyticBot
                    </h1>
                </div>

                <nav className="flex-1 space-y-2">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${location.pathname === item.path
                                    ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 text-blue-400'
                                    : 'hover:bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </Link>
                    ))}
                </nav>

                <div className="mt-auto pt-6 border-t border-white/10">
                    <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                                <User size={16} />
                            </div>
                            <div>
                                <p className="text-sm font-medium">{role === 'admin' ? 'Admin User' : 'Standard User'}</p>
                                <button
                                    onClick={() => setRole(role === 'admin' ? 'user' : 'admin')}
                                    className="text-xs text-blue-400 hover:text-blue-300"
                                >
                                    Switch Role
                                </button>
                            </div>
                        </div>
                        <Settings size={16} className="text-gray-400 cursor-pointer hover:text-white" />
                    </div>
                </div>
            </motion.div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto relative">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
                <div className="p-8 h-full">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Layout;
