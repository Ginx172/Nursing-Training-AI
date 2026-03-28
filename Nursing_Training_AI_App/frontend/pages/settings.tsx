import React, { useState, useEffect, FormEvent } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import ProtectedRoute from '../components/ProtectedRoute';
import api from '../lib/api';
import {
  User, Lock, Shield, ArrowLeft, Save, AlertCircle, CheckCircle, Loader2,
} from 'lucide-react';

function SettingsContent() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'security'>('profile');

  // Profile state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [nhsBand, setNhsBand] = useState('');
  const [yearsExperience, setYearsExperience] = useState(0);
  const [profileMsg, setProfileMsg] = useState('');
  const [profileError, setProfileError] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);

  // Password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSaving, setPasswordSaving] = useState(false);

  // 2FA state
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [twoFALoading, setTwoFALoading] = useState(true);

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setSpecialization(user.specialization || '');
      setNhsBand(user.nhs_band || '');
      setYearsExperience(user.years_experience || 0);
    }
  }, [user]);

  useEffect(() => {
    api.get('/api/auth/2fa/status')
      .then((res) => setTwoFAEnabled(res.data.enabled || false))
      .catch(() => {})
      .finally(() => setTwoFALoading(false));
  }, []);

  const handleProfileSave = async (e: FormEvent) => {
    e.preventDefault();
    setProfileMsg('');
    setProfileError('');
    setProfileSaving(true);

    try {
      await api.put('/api/users/me/profile', {
        first_name: firstName,
        last_name: lastName,
        specialization: specialization || null,
        nhs_band: nhsBand || null,
        years_experience: yearsExperience,
      });
      setProfileMsg('Profile updated successfully.');
      if (refreshUser) await refreshUser();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setProfileError(typeof detail === 'string' ? detail : 'Failed to update profile.');
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordChange = async (e: FormEvent) => {
    e.preventDefault();
    setPasswordMsg('');
    setPasswordError('');

    if (newPassword !== confirmNewPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setPasswordSaving(true);

    try {
      await api.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordMsg('Password changed successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setPasswordError(typeof detail === 'string' ? detail : 'Failed to change password.');
    } finally {
      setPasswordSaving(false);
    }
  };

  const tabs = [
    { id: 'profile' as const, label: 'Profile', icon: User },
    { id: 'password' as const, label: 'Password', icon: Lock },
    { id: 'security' as const, label: 'Security', icon: Shield },
  ];

  const nhsBands = ['band_2', 'band_3', 'band_4', 'band_5', 'band_6', 'band_7', 'band_8a', 'band_8b', 'band_8c', 'band_8d'];

  return (
    <>
      <Head>
        <title>Settings - Nursing Training AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-4">
            <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-gray-600">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-bold text-gray-900">Settings</h1>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex gap-8">
            {/* Sidebar tabs */}
            <div className="w-48 flex-shrink-0">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <form onSubmit={handleProfileSave} className="space-y-5">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h2>

                  {profileMsg && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-green-700">{profileMsg}</span>
                    </div>
                  )}
                  {profileError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <span className="text-sm text-red-700">{profileError}</span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input type="text" required value={firstName} onChange={(e) => setFirstName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input type="text" required value={lastName} onChange={(e) => setLastName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" disabled value={user?.email || ''} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500" />
                    <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">NHS Band</label>
                      <select value={nhsBand} onChange={(e) => setNhsBand(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        <option value="">Not set</option>
                        {nhsBands.map((b) => (
                          <option key={b} value={b}>{b.replace('_', ' ').toUpperCase()}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Years Experience</label>
                      <input type="number" min="0" max="50" value={yearsExperience} onChange={(e) => setYearsExperience(parseInt(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                    <input type="text" value={specialization} onChange={(e) => setSpecialization(e.target.value)}
                      placeholder="e.g. AMU, Emergency, Pediatrics"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                  </div>

                  <button type="submit" disabled={profileSaving}
                    className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50">
                    {profileSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    {profileSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </form>
              )}

              {/* Password Tab */}
              {activeTab === 'password' && (
                <form onSubmit={handlePasswordChange} className="space-y-5">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h2>

                  {passwordMsg && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-green-700">{passwordMsg}</span>
                    </div>
                  )}
                  {passwordError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <span className="text-sm text-red-700">{passwordError}</span>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                    <input type="password" required value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" autoComplete="current-password" />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                    <input type="password" required value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Min 12 characters (NHS policy)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" autoComplete="new-password" />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                    <input type="password" required value={confirmNewPassword} onChange={(e) => setConfirmNewPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" autoComplete="new-password" />
                  </div>

                  <button type="submit" disabled={passwordSaving}
                    className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50">
                    {passwordSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                    {passwordSaving ? 'Changing...' : 'Change Password'}
                  </button>
                </form>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="space-y-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h2>

                  {/* 2FA Section */}
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">Two-Factor Authentication (2FA)</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Add an extra layer of security with TOTP authenticator app
                        </p>
                      </div>
                      {twoFALoading ? (
                        <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                      ) : (
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          twoFAEnabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {twoFAEnabled ? 'Enabled' : 'Disabled'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Email Verification Section */}
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">Email Verification</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Verify your email address to unlock all features
                        </p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user?.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {user?.is_verified ? 'Verified' : 'Not Verified'}
                      </span>
                    </div>
                    {!user?.is_verified && (
                      <button
                        onClick={async () => {
                          try {
                            await api.post('/api/auth/send-verification');
                            alert('Verification email sent. Check your inbox.');
                          } catch {
                            alert('Failed to send verification email.');
                          }
                        }}
                        className="mt-3 text-sm text-blue-600 font-medium hover:underline"
                      >
                        Send verification email
                      </button>
                    )}
                  </div>

                  {/* Account Info */}
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="font-medium text-gray-900">Account</h3>
                    <div className="mt-2 space-y-1 text-sm text-gray-500">
                      <p>Role: <span className="text-gray-700 font-medium">{user?.role}</span></p>
                      <p>Subscription: <span className="text-gray-700 font-medium">{user?.subscription_tier}</span></p>
                      <p>Member since: <span className="text-gray-700 font-medium">
                        {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                      </span></p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}
