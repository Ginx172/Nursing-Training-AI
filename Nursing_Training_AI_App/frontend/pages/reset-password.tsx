import React, { useState, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import api from '../lib/api';
import { Lock, ArrowLeft, CheckCircle, AlertCircle, Stethoscope } from 'lucide-react';

export default function ResetPasswordPage() {
  const router = useRouter();
  const { token } = router.query;

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const passwordChecks = [
    { label: 'At least 12 characters', pass: password.length >= 12 },
    { label: 'One uppercase letter', pass: /[A-Z]/.test(password) },
    { label: 'One lowercase letter', pass: /[a-z]/.test(password) },
    { label: 'One digit', pass: /\d/.test(password) },
    { label: 'Passwords match', pass: password.length > 0 && password === confirmPassword },
  ];

  const allChecksPassed = passwordChecks.every((c) => c.pass);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!token) {
      setError('Invalid reset link. Please request a new one.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);

    try {
      await api.post('/api/auth/reset-password', {
        token: token as string,
        new_password: password,
      });
      setSuccess(true);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 429) {
        setError('Too many attempts. Please wait before trying again.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Reset failed. The link may have expired.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Head>
        <title>Reset Password - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
              <Stethoscope className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Set New Password</h1>
            <p className="text-gray-500 mt-1">Choose a strong password for your account</p>
          </div>

          {success ? (
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Password Reset Complete</h2>
              <p className="text-gray-500 mb-6">
                Your password has been updated. You can now sign in with your new password.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Go to Login
              </Link>
            </div>
          ) : (
            <>
              {!token && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-700">
                    Invalid or missing reset token. Please use the link from your email, or{' '}
                    <Link href="/forgot-password" className="underline font-medium">
                      request a new one
                    </Link>.
                  </p>
                </div>
              )}

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
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                    New Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                    placeholder="Min 12 characters (NHS policy)"
                    autoComplete="new-password"
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm New Password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                    placeholder="Confirm your password"
                    autoComplete="new-password"
                  />
                </div>

                {/* Password strength indicators */}
                {password.length > 0 && (
                  <div className="space-y-1.5">
                    {passwordChecks.map((check, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <span className={check.pass ? 'text-green-500' : 'text-gray-300'}>
                          {check.pass ? '\u2713' : '\u2022'}
                        </span>
                        <span className={check.pass ? 'text-green-700' : 'text-gray-500'}>
                          {check.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isSubmitting || !token || !allChecksPassed}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <span className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    <Lock className="w-5 h-5" />
                  )}
                  {isSubmitting ? 'Resetting...' : 'Reset Password'}
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
