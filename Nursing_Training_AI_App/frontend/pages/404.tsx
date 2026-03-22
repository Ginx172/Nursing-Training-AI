import React from 'react';
import { NextPage } from 'next';
import Link from 'next/link';
import { FileQuestion } from 'lucide-react';

const Custom404: NextPage = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md text-center border border-slate-100">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <FileQuestion className="h-8 w-8 text-indigo-600" />
                </div>

                <h1 className="text-3xl font-bold text-slate-800 mb-2">Page Not Found</h1>

                <p className="text-slate-500 mb-8 leading-relaxed">
                    The page you are looking for does not exist or has been moved.
                </p>

                <Link href="/dashboard" className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition shadow-lg shadow-indigo-200">
                    Return to Dashboard
                </Link>
            </div>
        </div>
    );
};

export default Custom404;
