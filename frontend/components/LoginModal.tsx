'use client';

import React, { FormEvent, useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  Mail,
  ShieldCheck,
  UserRound,
  X,
} from 'lucide-react';
import { AuthenticatedUser, AuthServiceError, login, register, requestPasswordReset } from '../lib/auth';
import { isValidEmail } from '../lib/authValidation';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: AuthenticatedUser) => void;
}

type AuthScreen = 'signin' | 'register' | 'reset';
type FieldErrors = Partial<Record<'name' | 'email' | 'password' | 'confirmPassword', string>>;

const inputClassName =
  'w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 outline-none transition focus-visible:border-fuchsia-400 focus-visible:ring-2 focus-visible:ring-fuchsia-400/40';
const secondaryButtonClassName =
  'font-semibold text-fuchsia-300 underline-offset-4 transition hover:text-fuchsia-200 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 disabled:opacity-50';

export default function LoginModal({ isOpen, onClose, onLoginSuccess }: LoginModalProps) {
  const [screen, setScreen] = useState<AuthScreen>('signin');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState('');
  const [messageIsSuccess, setMessageIsSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const emailInputRef = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  const clearFeedback = useCallback(() => {
    setFieldErrors({});
    setMessage('');
    setMessageIsSuccess(false);
  }, []);

  const closeModal = useCallback(() => {
    if (isLoading) return;
    setPassword('');
    setConfirmPassword('');
    setShowPassword(false);
    setShowConfirmPassword(false);
    clearFeedback();
    onClose();
  }, [clearFeedback, isLoading, onClose]);

  useEffect(() => {
    if (!isOpen) return;

    emailInputRef.current?.focus();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !isLoading) {
        closeModal();
      }
      if (event.key !== 'Tab') return;

      const focusableElements = dialogRef.current?.querySelectorAll<HTMLElement>(
        'button:not(:disabled), input:not(:disabled), a[href]',
      );
      if (!focusableElements?.length) return;
      const first = focusableElements[0];
      const last = focusableElements[focusableElements.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeModal, isOpen, isLoading]);

  if (!isOpen) return null;

  const switchScreen = (nextScreen: AuthScreen) => {
    if (isLoading) return;
    setScreen(nextScreen);
    setPassword('');
    setConfirmPassword('');
    setShowPassword(false);
    setShowConfirmPassword(false);
    clearFeedback();
  };

  const showServiceError = (error: unknown, operation: 'LOGIN' | 'REGISTER' | 'RESET') => {
    if (error instanceof AuthServiceError && error.code === 'INVALID_CREDENTIALS') {
      setMessage('The email address or password is incorrect. Please try again.');
      return;
    }
    if (error instanceof AuthServiceError && error.code === 'ACCOUNT_EXISTS') {
      setMessage('An account with this email already exists. Sign in instead.');
      return;
    }
    if (error instanceof AuthServiceError && error.code === 'RESET_NOT_CONFIGURED') {
      setMessage('Password reset is not available yet because email delivery has not been configured.');
      return;
    }
    if (error instanceof AuthServiceError && error.code === 'SERVICE_UNAVAILABLE') {
      setMessage('The authentication service is unavailable. Check the backend and database configuration.');
      return;
    }
    setMessage(
      operation === 'RESET'
        ? 'We could not send a reset link. Please try again later.'
        : 'We could not complete your request. Please try again.',
    );
  };

  const handleSignIn = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearFeedback();

    const errors: FieldErrors = {};
    if (!email.trim()) errors.email = 'Enter your email address.';
    else if (!isValidEmail(email.trim())) errors.email = 'Enter a valid email address.';
    if (!password) errors.password = 'Enter your password.';
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      const user = await login({ email: email.trim(), password, rememberMe });
      setPassword('');
      onLoginSuccess({
        name: user.name || user.email || email.trim(),
        email: user.email || email.trim(),
      });
      onClose();
    } catch (error) {
      showServiceError(error, 'LOGIN');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearFeedback();

    const errors: FieldErrors = {};
    if (fullName.trim().length < 2) errors.name = 'Enter your full name.';
    if (!email.trim()) errors.email = 'Enter your email address.';
    else if (!isValidEmail(email.trim())) errors.email = 'Enter a valid email address.';
    if (password.length < 8 || !/[a-z]/i.test(password) || !/\d/.test(password)) {
      errors.password = 'Use at least 8 characters, including a letter and a number.';
    }
    if (!confirmPassword) errors.confirmPassword = 'Confirm your password.';
    else if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match.';
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      await register({ fullName: fullName.trim(), email: email.trim(), password });
      setMessage('Your account request was accepted. Follow any instructions from your authentication service before signing in.');
      setMessageIsSuccess(true);
      setPassword('');
      setConfirmPassword('');
    } catch (error) {
      showServiceError(error, 'REGISTER');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearFeedback();

    const errors: FieldErrors = {};
    if (!email.trim()) errors.email = 'Enter your email address.';
    else if (!isValidEmail(email.trim())) errors.email = 'Enter a valid email address.';
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      await requestPasswordReset(email.trim());
      setMessage('If this email is registered, password reset instructions have been sent.');
      setMessageIsSuccess(true);
    } catch (error) {
      showServiceError(error, 'RESET');
    } finally {
      setIsLoading(false);
    }
  };

  const passwordGuidance = [
    { label: 'At least 8 characters', met: password.length >= 8 },
    { label: 'At least one letter', met: /[a-z]/i.test(password) },
    { label: 'At least one number', met: /\d/.test(password) },
  ];

  const renderPasswordInput = (
    id: string,
    label: string,
    value: string,
    onChange: (value: string) => void,
    visible: boolean,
    setVisible: (visible: boolean) => void,
    error?: string,
    autoComplete: 'current-password' | 'new-password' = 'current-password',
  ) => (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-slate-200">
        {label}
      </label>
      <div className="relative">
        <LockKeyhole
          aria-hidden="true"
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
        />
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          autoComplete={autoComplete}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          aria-required="true"
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${id}-error` : undefined}
          className={`${inputClassName} pl-10 pr-12`}
        />
        <button
          type="button"
          onClick={() => setVisible(!visible)}
          aria-label={`${visible ? 'Hide' : 'Show'} ${label.toLowerCase()}`}
          aria-pressed={visible}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-400 transition hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400"
        >
          {visible ? <EyeOff aria-hidden="true" className="h-4 w-4" /> : <Eye aria-hidden="true" className="h-4 w-4" />}
        </button>
      </div>
      {error && (
        <p id={`${id}-error`} className="mt-1.5 text-xs text-rose-300" role="alert">
          {error}
        </p>
      )}
    </div>
  );

  const renderEmailInput = (label = 'Email address') => (
    <div>
      <label htmlFor="auth-email" className="mb-1.5 block text-sm font-medium text-slate-200">
        {label}
      </label>
      <div className="relative">
        <Mail
          aria-hidden="true"
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
        />
        <input
          ref={emailInputRef}
          id="auth-email"
          type="email"
          inputMode="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          aria-required="true"
          aria-invalid={Boolean(fieldErrors.email)}
          aria-describedby={fieldErrors.email ? 'auth-email-error' : undefined}
          placeholder="you@example.com"
          className={`${inputClassName} pl-10`}
        />
      </div>
      {fieldErrors.email && (
        <p id="auth-email-error" className="mt-1.5 text-xs text-rose-300" role="alert">
          {fieldErrors.email}
        </p>
      )}
    </div>
  );

  const renderSubmitButton = (label: string, loadingLabel: string) => (
    <button
      type="submit"
      disabled={isLoading}
      className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-purple-950/40 transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 active:scale-[0.99] disabled:cursor-wait disabled:opacity-70"
    >
      {isLoading ? (
        <>
          <LoaderCircle aria-hidden="true" className="h-4 w-4 animate-spin" />
          {loadingLabel}
        </>
      ) : (
        <>
          {label}
          <ArrowRight aria-hidden="true" className="h-4 w-4" />
        </>
      )}
    </button>
  );

  const title =
    screen === 'signin' ? 'Welcome back' : screen === 'register' ? 'Create your account' : 'Reset your password';
  const subtitle =
    screen === 'signin'
      ? 'Sign in to continue with TrustRoute.'
      : screen === 'register'
        ? 'Plan smarter journeys with your TrustRoute account.'
        : 'We’ll help you get back on the road.';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/80 p-3 backdrop-blur-md sm:p-5">
      <motion.div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        aria-describedby="auth-subtitle"
        initial={{ opacity: 0, scale: 0.96, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="relative my-auto w-full max-w-md overflow-hidden rounded-3xl border border-slate-700/80 bg-slate-900 shadow-2xl shadow-purple-950/50"
      >
        <div aria-hidden="true" className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />
        <button
          type="button"
          onClick={closeModal}
          disabled={isLoading}
          aria-label="Close authentication"
          className="absolute right-4 top-4 z-10 rounded-full p-2 text-slate-400 transition hover:bg-slate-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400 disabled:opacity-50 sm:right-5 sm:top-5"
        >
          <X aria-hidden="true" className="h-5 w-5" />
        </button>

        <div className="px-5 pb-6 pt-8 sm:px-8 sm:pb-8 sm:pt-9">
          {screen !== 'signin' && (
            <button
              type="button"
              onClick={() => switchScreen('signin')}
              disabled={isLoading}
              className="mb-5 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 transition hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400 disabled:opacity-50"
            >
              <ArrowLeft aria-hidden="true" className="h-3.5 w-3.5" />
              Back to Sign In
            </button>
          )}

          <div className="mb-6 text-center">
            <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-indigo-400/30 bg-indigo-500/15 text-indigo-300">
              <ShieldCheck aria-hidden="true" className="h-6 w-6" />
            </div>
            <h2 id="auth-title" className="text-xl font-bold text-white">
              {title}
            </h2>
            <p id="auth-subtitle" className="mt-1.5 text-sm text-slate-400">
              {subtitle}
            </p>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={screen}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.16 }}
            >
              {screen === 'signin' && (
                <form noValidate onSubmit={handleSignIn} className="space-y-4">
                  {renderEmailInput()}
                  {renderPasswordInput(
                    'auth-password',
                    'Password',
                    password,
                    setPassword,
                    showPassword,
                    setShowPassword,
                    fieldErrors.password,
                  )}

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-0.5">
                    <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        checked={rememberMe}
                        onChange={(event) => setRememberMe(event.target.checked)}
                        className="h-4 w-4 rounded border-slate-600 bg-slate-950 text-fuchsia-500 accent-fuchsia-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400"
                      />
                      Remember me
                    </label>
                    <button
                      type="button"
                      onClick={() => switchScreen('reset')}
                      disabled={isLoading}
                      className={secondaryButtonClassName}
                    >
                      Forgot password?
                    </button>
                  </div>

                  {message && (
                    <p
                      role={messageIsSuccess ? 'status' : 'alert'}
                      className={`rounded-xl border px-3.5 py-3 text-sm ${
                        messageIsSuccess
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                          : 'border-rose-500/30 bg-rose-500/10 text-rose-200'
                      }`}
                    >
                      {message}
                    </p>
                  )}

                  {renderSubmitButton('Sign In', 'Signing in…')}
                  <p className="pt-1 text-center text-sm text-slate-400">
                    Don&apos;t have an account?{' '}
                    <button
                      type="button"
                      onClick={() => switchScreen('register')}
                      disabled={isLoading}
                      className={secondaryButtonClassName}
                    >
                      Create account
                    </button>
                  </p>
                </form>
              )}

              {screen === 'register' && (
                <form noValidate onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <label htmlFor="auth-full-name" className="mb-1.5 block text-sm font-medium text-slate-200">
                      Full name
                    </label>
                    <div className="relative">
                      <UserRound
                        aria-hidden="true"
                        className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
                      />
                      <input
                        id="auth-full-name"
                        type="text"
                        autoComplete="name"
                        value={fullName}
                        onChange={(event) => setFullName(event.target.value)}
                        aria-required="true"
                        aria-invalid={Boolean(fieldErrors.name)}
                        aria-describedby={fieldErrors.name ? 'auth-name-error' : undefined}
                        placeholder="Your name"
                        className={`${inputClassName} pl-10`}
                      />
                    </div>
                    {fieldErrors.name && (
                      <p id="auth-name-error" className="mt-1.5 text-xs text-rose-300" role="alert">
                        {fieldErrors.name}
                      </p>
                    )}
                  </div>
                  {renderEmailInput()}
                  {renderPasswordInput(
                    'auth-password',
                    'Password',
                    password,
                    setPassword,
                    showPassword,
                    setShowPassword,
                    fieldErrors.password,
                    'new-password',
                  )}
                  <ul aria-label="Password requirements" className="space-y-1 text-xs">
                    {passwordGuidance.map((requirement) => (
                      <li
                        key={requirement.label}
                        className={requirement.met ? 'text-emerald-300' : 'text-slate-400'}
                      >
                        <span aria-hidden="true">{requirement.met ? '✓' : '•'}</span>{' '}
                        {requirement.label}
                      </li>
                    ))}
                  </ul>
                  {renderPasswordInput(
                    'auth-confirm-password',
                    'Confirm password',
                    confirmPassword,
                    setConfirmPassword,
                    showConfirmPassword,
                    setShowConfirmPassword,
                    fieldErrors.confirmPassword,
                    'new-password',
                  )}

                  {message && (
                    <p
                      role={messageIsSuccess ? 'status' : 'alert'}
                      className={`rounded-xl border px-3.5 py-3 text-sm ${
                        messageIsSuccess
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                          : 'border-rose-500/30 bg-rose-500/10 text-rose-200'
                      }`}
                    >
                      {message}
                    </p>
                  )}

                  {renderSubmitButton('Create Account', 'Creating account…')}
                  <p className="pt-1 text-center text-sm text-slate-400">
                    Already have an account?{' '}
                    <button
                      type="button"
                      onClick={() => switchScreen('signin')}
                      disabled={isLoading}
                      className={secondaryButtonClassName}
                    >
                      Sign In
                    </button>
                  </p>
                </form>
              )}

              {screen === 'reset' && (
                <form noValidate onSubmit={handleReset} className="space-y-4">
                  {renderEmailInput()}
                  {message && (
                    <p
                      role={messageIsSuccess ? 'status' : 'alert'}
                      className={`rounded-xl border px-3.5 py-3 text-sm ${
                        messageIsSuccess
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                          : 'border-rose-500/30 bg-rose-500/10 text-rose-200'
                      }`}
                    >
                      {message}
                    </p>
                  )}
                  {renderSubmitButton('Send reset link', 'Sending…')}
                </form>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
