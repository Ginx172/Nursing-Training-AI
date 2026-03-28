import React, { useState, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import api from '../lib/api';
import { Mail, ArrowLeft, CheckCircle, AlertCircle, Stethoscope } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await api.post('/api/auth/forgot-password', { email });
      setSuccess(true);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 429) {
        setError('Too many requests. Please wait a few minutes before trying again.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Head>
        <title>Forgot Password - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
              <Stethoscope className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Reset Your Password</h1>
            <p className="text-gray-500 mt-1">
              Enter your email and we'll send you a reset link
            </p>
          </div>

          {success ? (
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Check Your Email</h2>
              <p className="text-gray-500 mb-6">
                If an account with that email exists, we've sent a password reset link.
                Please check your inbox and spam folder.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-blue-600 font-medium hover:underline"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to login
              </Link>
            </div>
          ) : (
            <>
              {/* Error message */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email address
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                    placeholder="nurse@nhs.net"
                    autoComplete="email"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <span className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    <Mail className="w-5 h-5" />
                  )}
                  {isSubmitting ? 'Sending...' : 'Send Reset Link'}
                </button>
              </form>

              {/* Footer */}
              <div className="mt-6 text-center">
                <Link href="/login" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
                  <ArrowLeft className="w-4 h-4" />
                  Back to login
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
