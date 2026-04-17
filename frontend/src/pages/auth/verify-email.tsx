import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { CheckCircle2, AlertCircle, Loader2, Mail, Brain } from 'lucide-react'
import apiClient from '@/lib/api'

export default function VerifyEmail() {
  const router = useRouter()
  const { token } = router.query

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    if (!token) return

    const verifyToken = async () => {
      try {
        // Call backend to verify email token
        const response = await apiClient.post('/api/v1/auth/verify-email', { token })
        
        setStatus('success')
        setEmail(response.data.email || '')
        setMessage(response.data.message || 'Email verified successfully!')

        // Auto-redirect to dashboard after 3 seconds
        setTimeout(() => {
          router.push('/dashboard')
        }, 3000)
      } catch (error: any) {
        setStatus('error')
        setMessage(
          error.response?.data?.detail || 
          'Email verification failed. The link may have expired or is invalid.'
        )
      }
    }

    verifyToken()
  }, [token, router])

  return (
    <>
      <Head>
        <title>Verify Email | PrepEdge AI</title>
        <meta name="description" content="Email verification" />
      </Head>

      <div className="min-h-screen flex flex-row-reverse">
        {/* Left side - Decorative */}
        <div className="hidden lg:flex flex-1 items-center justify-center relative bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 p-8">
          <div className="absolute inset-0 opacity-20">
            <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full mix-blend-multiply filter blur-3xl"></div>
            <div className="absolute bottom-20 right-10 w-72 h-72 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl"></div>
          </div>
          
          <div className="relative z-10 text-center">
            <Mail className="w-32 h-32 text-white/80 mx-auto mb-6" />
            <h2 className="text-4xl font-bold text-white mb-4">Secure Access</h2>
            <p className="text-white/90 text-lg">Verify your email to unlock all PrepEdge AI features</p>
          </div>
        </div>

        {/* Right side - Verification */}
        <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 bg-white">
          <div className="absolute top-8 left-8">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-xl">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-xl tracking-tight text-slate-800">
                PrepEdge AI
              </span>
            </Link>
          </div>

          <div className="mx-auto w-full max-w-sm lg:w-[28rem] pt-16 lg:pt-0">
            {status === 'loading' && (
              <div className="text-center py-12">
                <div className="flex justify-center mb-6">
                  <Loader2 className="w-16 h-16 text-indigo-500 animate-spin" />
                </div>
                <h2 className="text-2xl font-heading font-bold text-slate-900 mb-2">
                  Verifying Email
                </h2>
                <p className="text-slate-600">Please wait while we verify your email address...</p>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center py-8">
                <div className="flex justify-center mb-6">
                  <div className="relative">
                    <div className="absolute inset-0 bg-emerald-200 rounded-full blur-xl opacity-30"></div>
                    <CheckCircle2 className="w-20 h-20 text-emerald-500 relative" />
                  </div>
                </div>
                <h2 className="text-3xl font-heading font-bold text-slate-900 mb-2">
                  Email Verified! ✓
                </h2>
                <p className="text-slate-600 mb-6">
                  {email && <span>Thank you, <span className="font-semibold">{email}</span>!</span>}
                  <br />
                  Your account is now fully activated.
                </p>

                <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-xl mb-8">
                  <p className="text-sm text-emerald-800">
                    ✓ Email confirmed<br />
                    ✓ Account activated<br />
                    ✓ Ready to start!
                  </p>
                </div>

                <div className="space-y-3">
                  <p className="text-sm text-slate-600">
                    Redirecting to dashboard in 3 seconds...
                  </p>
                  <Link
                    href="/dashboard"
                    className="block w-full px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-300 text-center"
                  >
                    Go to Dashboard
                  </Link>
                </div>
              </div>
            )}

            {status === 'error' && (
              <div className="text-center py-8">
                <div className="flex justify-center mb-6">
                  <div className="relative">
                    <div className="absolute inset-0 bg-red-200 rounded-full blur-xl opacity-30"></div>
                    <AlertCircle className="w-20 h-20 text-red-500 relative" />
                  </div>
                </div>
                <h2 className="text-3xl font-heading font-bold text-slate-900 mb-2">
                  Verification Failed
                </h2>
                <p className="text-slate-600 mb-6">
                  {message}
                </p>

                <div className="p-6 bg-red-50 border border-red-200 rounded-xl mb-8">
                  <p className="text-sm text-red-800 mb-4">
                    <strong>Why this might happen:</strong>
                  </p>
                  <ul className="text-sm text-red-700 space-y-2 text-left">
                    <li>• The link has expired (usually valid for 24 hours)</li>
                    <li>• The link has already been used</li>
                    <li>• The email address is incorrect</li>
                    <li>• There was a network error</li>
                  </ul>
                </div>

                <div className="space-y-3">
                  <Link
                    href="/auth/register"
                    className="block w-full px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-300 text-center"
                  >
                    Create New Account
                  </Link>
                  <Link
                    href="/"
                    className="block w-full px-6 py-3 border border-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-all duration-300 text-center"
                  >
                    Back to Home
                  </Link>
                </div>

                <p className="mt-6 text-sm text-slate-600">
                  Need help?{' '}
                  <Link href="/contact" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                    Contact Support
                  </Link>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
