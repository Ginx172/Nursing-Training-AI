import React from 'react';
import { NextPage } from 'next';
import { AlertCircle } from 'lucide-react';

interface ErrorProps {
    statusCode?: number;
}

const Error: NextPage<ErrorProps> = ({ statusCode }) => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md text-center border border-slate-100">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <AlertCircle className="h-8 w-8 text-red-600" />
                </div>

                <h1 className="text-3xl font-bold text-slate-800 mb-2">
                    {statusCode ? `Error ${statusCode}` : 'Client Error'}
                </h1>

                <p className="text-slate-500 mb-8 leading-relaxed">
                    {statusCode
                        ? `An error occurred on the server`
                        : 'An error occurred on the client'}
                </p>

                <button
                    onClick={() => window.location.reload()}
                    className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition shadow-lg shadow-indigo-200"
                >
                    Refresh Page
                </button>
            </div>
        </div>
    );
};

Error.getInitialProps = ({ res, err }) => {
    const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
    return { statusCode };
};

export default Error;
