import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import api from '../lib/api';
import { CheckCircle, XCircle, Loader2, Stethoscope } from 'lucide-react';

export default function VerifyEmailPage() {
  const router = useRouter();
  const { token } = router.query;

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) return;

    const verify = async () => {
      try {
        const res = await api.post(`/api/auth/verify-email?token=${token}`);
        setMessage(res.data.message || 'Email verified successfully!');
        setStatus('success');
      } catch (err: any) {
        const detail = err?.response?.data?.detail;
        setMessage(typeof detail === 'string' ? detail : 'Verification failed. The link may have expired.');
        setStatus('error');
      }
    };

    verify();
  }, [token]);

  return (
    <>
      <Head>
        <title>Verify Email - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-6">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>

          {!token && status === 'loading' ? (
            <>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Invalid Link</h1>
              <p className="text-gray-500 mb-6">
                No verification token found. Please use the link from your email.
              </p>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Go to Dashboard
              </Link>
            </>
          ) : status === 'loading' ? (
            <>
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Verifying Email...</h1>
              <p className="text-gray-500">Please wait while we verify your email address.</p>
            </>
          ) : status === 'success' ? (
            <>
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Email Verified</h1>
              <p className="text-gray-500 mb-6">{message}</p>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Go to Dashboard
              </Link>
            </>
          ) : (
            <>
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h1>
              <p className="text-gray-500 mb-6">{message}</p>
              <Link
                href="/login"
                className="inline-flex items-center justify-center bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Go to Login
              </Link>
            </>
          )}
        </div>
      </div>
    </>
  );
}
