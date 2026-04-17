import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Register from '@/pages/auth/register'
import { useAuthStore } from '@/store/auth'

// Mock the router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

// Mock the API
jest.mock('@/lib/api', () => ({
  authApi: {
    register: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}))

describe('Register Page', () => {
  it('renders the registration form', () => {
    render(<Register />)
    
    expect(screen.getByText('Create an account')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('John Doe')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('john@example.com')).toBeInTheDocument()
  })

  it('has all required fields', () => {
    render(<Register />)
    
    expect(screen.getByText('Full Name')).toBeInTheDocument()
    expect(screen.getByText('Username')).toBeInTheDocument()
    expect(screen.getByText('Email address')).toBeInTheDocument()
    expect(screen.getByText('Password')).toBeInTheDocument()
    expect(screen.getByText('College/University (Optional)')).toBeInTheDocument()
    expect(screen.getByText('Course/Major (Optional)')).toBeInTheDocument()
    expect(screen.getByText('Years of Experience (Optional)')).toBeInTheDocument()
  })

  it('displays password strength indicator', () => {
    render(<Register />)
    
    const passwordInput = screen.getByPlaceholderText('••••••••')
    fireEvent.change(passwordInput, { target: { value: 'weak' } })
    
    expect(screen.getByText('Too weak')).toBeInTheDocument()
  })

  it('shows stronger password as input improves', () => {
    render(<Register />)
    
    const passwordInput = screen.getByPlaceholderText('••••••••')
    fireEvent.change(passwordInput, { target: { value: 'StrongPass123!' } })
    
    expect(screen.getByText('Strong')).toBeInTheDocument()
  })

  it('has social login buttons', () => {
    render(<Register />)
    
    expect(screen.getByText('Google')).toBeInTheDocument()
    expect(screen.getByText('GitHub')).toBeInTheDocument()
  })

  it('has link to login page', () => {
    render(<Register />)
    
    const loginLink = screen.getByText(/already have an account/i)
    expect(loginLink).toBeInTheDocument()
  })
})

describe('Login Page', () => {
  it('renders the login form', () => {
    const { default: Login } = require('@/pages/auth/login')
    render(<Login />)
    
    expect(screen.getByText('Welcome back')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument()
  })

  it('has social login options', () => {
    const { default: Login } = require('@/pages/auth/login')
    render(<Login />)
    
    expect(screen.getByText('Google')).toBeInTheDocument()
    expect(screen.getByText('GitHub')).toBeInTheDocument()
  })

  it('has forgot password link', () => {
    const { default: Login } = require('@/pages/auth/login')
    render(<Login />)
    
    expect(screen.getByText(/forgot password/i)).toBeInTheDocument()
  })
})

describe('Zustand Auth Store', () => {
  it('should initialize with no user', () => {
    const { isAuthenticated } = useAuthStore.getState()
    // Initial state should not be authenticated
    expect(isAuthenticated).toBe(false)
  })

  it('should login user', () => {
    const { login } = useAuthStore.getState()
    const testUser = { id: 1, email: 'test@example.com', username: 'testuser' }
    
    login(testUser, 'fake-token')
    const { user, isAuthenticated } = useAuthStore.getState()
    
    expect(isAuthenticated).toBe(true)
    expect(user).toEqual(testUser)
  })

  it('should logout user', () => {
    const { login, logout } = useAuthStore.getState()
    login({ id: 1, email: 'test@example.com' }, 'token')
    logout()
    
    const { isAuthenticated } = useAuthStore.getState()
    expect(isAuthenticated).toBe(false)
  })
})
