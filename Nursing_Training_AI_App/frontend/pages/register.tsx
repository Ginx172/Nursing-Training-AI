import React, { useState, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { UserPlus, AlertCircle, CheckCircle, Stethoscope } from 'lucide-react';

const NHS_BANDS = [
  { value: '', label: 'Select NHS Band (optional)' },
  { value: 'band_2', label: 'Band 2' },
  { value: 'band_3', label: 'Band 3' },
  { value: 'band_4', label: 'Band 4' },
  { value: 'band_5', label: 'Band 5' },
  { value: 'band_6', label: 'Band 6' },
  { value: 'band_7', label: 'Band 7' },
  { value: 'band_8a', label: 'Band 8a' },
  { value: 'band_8b', label: 'Band 8b' },
  { value: 'band_8c', label: 'Band 8c' },
  { value: 'band_8d', label: 'Band 8d' },
  { value: 'band_9', label: 'Band 9' },
];

const SPECIALIZATIONS = [
  '', 'AMU/MAU', 'Emergency/A&E', 'ICU/Critical Care', 'Maternity',
  'Mental Health', 'Pediatrics', 'Surgical', 'Oncology', 'Community',
  'District Nursing', 'General Practice', 'Other',
];

export default function RegisterPage() {
  const router = useRouter();
  const { register, isAuthenticated } = useAuth();

  const [form, setForm] = useState({
    email: '', username: '', password: '', confirmPassword: '',
    first_name: '', last_name: '', nhs_band: '', specialization: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  React.useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard');
  }, [isAuthenticated, router]);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  // Validari parola in timp real
  const pw = form.password;
  const pwChecks = {
    length: pw.length >= 12,
    upper: /[A-Z]/.test(pw),
    lower: /[a-z]/.test(pw),
    digit: /\d/.test(pw),
    match: pw.length > 0 && pw === form.confirmPassword,
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        email: form.email,
        username: form.username,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        nhs_band: form.nhs_band || undefined,
        specialization: form.specialization || undefined,
      });
      router.push('/dashboard');
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const PwCheck = ({ ok, label }: { ok: boolean; label: string }) => (
    <div className={`flex items-center gap-1.5 text-xs ${ok ? 'text-green-600' : 'text-gray-400'}`}>
      {ok ? <CheckCircle className="w-3.5 h-3.5" /> : <span className="w-3.5 h-3.5 rounded-full border border-gray-300 inline-block" />}
      {label}
    </div>
  );

  return (
    <>
      <Head>
        <title>Register - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
        <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
              <Stethoscope className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
            <p className="text-gray-500 mt-1">Join Nursing Training AI</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name row */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">First name</label>
                <input id="first_name" type="text" required value={form.first_name} onChange={set('first_name')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm" />
              </div>
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">Last name</label>
                <input id="last_name" type="text" required value={form.last_name} onChange={set('last_name')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm" />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input id="email" type="email" required value={form.email} onChange={set('email')} autoComplete="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                placeholder="nurse@nhs.net" />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input id="username" type="text" required value={form.username} onChange={set('username')} autoComplete="username"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                placeholder="e.g. sarah_j" pattern="[a-zA-Z0-9_-]+" title="Letters, numbers, underscores, hyphens only" />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input id="password" type="password" required value={form.password} onChange={set('password')} autoComplete="new-password"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                placeholder="Min 12 characters (NHS security policy)" />
              {pw.length > 0 && (
                <div className="mt-2 grid grid-cols-2 gap-1">
                  <PwCheck ok={pwChecks.length} label="12+ characters" />
                  <PwCheck ok={pwChecks.upper} label="Uppercase letter" />
                  <PwCheck ok={pwChecks.lower} label="Lowercase letter" />
                  <PwCheck ok={pwChecks.digit} label="Digit" />
                </div>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">Confirm password</label>
              <input id="confirmPassword" type="password" required value={form.confirmPassword} onChange={set('confirmPassword')}
                autoComplete="new-password"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm ${
                  form.confirmPassword && !pwChecks.match ? 'border-red-300' : 'border-gray-300'
                }`} />
              {form.confirmPassword && !pwChecks.match && (
                <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
              )}
            </div>

            {/* NHS-specific fields */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="nhs_band" className="block text-sm font-medium text-gray-700 mb-1">NHS Band</label>
                <select id="nhs_band" value={form.nhs_band} onChange={set('nhs_band')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm bg-white">
                  {NHS_BANDS.map((b) => <option key={b.value} value={b.value}>{b.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="specialization" className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                <select id="specialization" value={form.specialization} onChange={set('specialization')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm bg-white">
                  {SPECIALIZATIONS.map((s) => <option key={s} value={s}>{s || 'Select (optional)'}</option>)}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !pwChecks.match || !pwChecks.length}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <UserPlus className="w-5 h-5" />
              )}
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            <span>Already have an account? </span>
            <Link href="/login" className="text-blue-600 font-medium hover:underline">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
